# app/main.py
from fastapi import FastAPI, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from sqlalchemy import func
from app.database import get_session, init_db
from app.models import Confession
from app.utils import paginate

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
init_db()


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    page: int = Query(1, ge=1),
    sort: str = Query("recent", regex="^(recent|top|random)$"),
    session: Session = Depends(get_session),
):
    pagination = paginate(session, Confession, page, page_size=3, sort=sort)

    total = session.exec(select(func.count()).select_from(Confession)).one()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "confessions": pagination["results"],
            "page": pagination["page"],
            "has_prev": pagination["has_prev"],
            "has_next": pagination["has_next"],
            "sort": sort,
            "total": total,
        },
    )

@app.get("/view", response_class=HTMLResponse)
def view_confessions(
    request: Request,
    page: int    = Query(1, ge=1),
    sort: str    = Query("recent", regex="^(recent|top|random)$"),
    session: Session = Depends(get_session),
):
    """
    Browse past confessions, paginated and sortable.
    """
    pagination = paginate(session, Confession, page, page_size=10, sort=sort)
    total = session.exec(select(func.count()).select_from(Confession)).one()
    return templates.TemplateResponse("view.html", {
        "request":     request,
        "confessions": pagination["results"],
        "page":        pagination["page"],
        "has_prev":    pagination["has_prev"],
        "has_next":    pagination["has_next"],
        "sort":        sort,
        "total":       total,
    })


@app.get("/about", response_class=HTMLResponse)
def about_page(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Explain the site, its purpose, and show total count.
    """
    total = session.exec(select(func.count()).select_from(Confession)).one()
    return templates.TemplateResponse("about.html", {
        "request": request,
        "total":   total,
    })


@app.post("/submit")
def submit_confession(
    content: str = Form(...), session: Session = Depends(get_session)
):
    confession = Confession(content=content)
    session.add(confession)
    session.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/upvote/{confession_id}")
def upvote_confession(
    confession_id: int,
    page: int = Query(1, ge=1),
    sort: str = Query("recent", regex="^(recent|top|random)$"),
    session: Session = Depends(get_session),
):
    confession = session.get(Confession, confession_id)
    if confession:
        confession.upvotes += 1
        session.add(confession)
        session.commit()
    return RedirectResponse(f"/?page={page}&sort={sort}", status_code=303)


# 3) Duel page (two random confessions to vote)
@app.get("/duel", response_class=HTMLResponse)
def duel(request: Request, session: Session = Depends(get_session)):
    total = session.exec(select(func.count()).select_from(Confession)).one()
    ids = session.exec(select(Confession.id).order_by(func.random()).limit(2)).all()
    if len(ids) < 2:
        return templates.TemplateResponse(
            "not_enough.html", {"request": request, "total": total}
        )
    a, b = [session.get(Confession, i) for i in ids]
    return templates.TemplateResponse(
        "duel.html", {"request": request, "a": a, "b": b, "total": total}
    )


# 4) Vote handler
@app.post("/duel/vote", response_class=HTMLResponse)
def vote(
    winner_id: int = Form(...),
    loser_id: int = Form(...),
    session: Session = Depends(get_session),
):
    # update score
    winner = session.get(Confession, winner_id)
    if winner:
        winner.score += 1
        session.add(winner)
        session.commit()

    # return a modal overlay
    return HTMLResponse(f"""
<div id="modal" class="modal">
  <div class="modal-content">
    <p>🗣️ The council has spoken!<br>
    Confession ID: #{winner.id} is the greater sin!</p>
    <p>
      <a href="/duel" class="button">Vote again</a>
      <a href="/"      class="button">Home</a>
    </p>
  </div>
</div>
""")
