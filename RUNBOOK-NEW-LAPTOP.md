# CITINEL console on a new laptop

Read this before touching any button on the live console. Four minutes.

The console at https://citinel-web.onrender.com can be **read by anyone** with
the link. It can be **changed only from a laptop that has been armed** with the
operator token. Arming lasts 12 hours on that laptop, then it forgets by
itself. Nothing on the server changes when you arm a laptop.

## A. Arm this laptop (every new laptop, and again after 12 hours)

1. Open https://dashboard.render.com and sign in. Only Danish has this login.
2. Click **citinel-web** in the left list.
3. Click **Environment** in the service's left menu.
4. Under **Environment Variables**, find the row `CITINEL_WRITE_TOKEN`.
5. Click the **eye** icon on that row, then the **copy** icon. The token is now on your clipboard.
6. Open https://citinel-web.onrender.com/Settings.dc.html
7. Find the row that starts with **ARM THIS DEVICE**.
8. First box: type your name (this name goes on every action you take).
9. Second box: paste the token (Cmd+V).
10. Click **SAVE**.
11. Look at the bottom of the left rail. It must show a green dot. Hover it and it reads **ARMED · YOUR NAME · EXPIRES hh:mm IST**.
    If it reads **READ-ONLY**, repeat steps 8 to 10.

That is all. Every screen now works. The rail's green dot is the only thing to
check before you click anything: green means go.

## B. If a button says "This device is not armed"

The 12 hours ran out, or someone pressed CLEAR, or you are on a different
laptop or browser. Do part A again. Ten seconds.

## C. Demo day

0. Someone with the repo runs `python3 scripts/preflight.py` in a terminal. It must print GO. If it prints NO-GO, it names the problem; send that line to Claude.
1. Arm the demo laptop (part A) in the morning. Once.
2. Check the green dot before going on stage.
3. Do **not** click **RUN THE SWARM** unless the demo script calls for a live run. It spends real credits and replaces the incident's existing verdict with a fresh one.
4. After the event: open Settings and press **CLEAR**, or better, rotate `CITINEL_WRITE_TOKEN` in Render, which makes every laptop forget at once.

## D. Things you do NOT need to redo

These were run once against production on 4 Sep 2026 and their results live on
the server's disk. A new laptop sees them immediately:

- the Gemini wide-lens sweep and the Tavily context on INC-0417
- the swarm verdict on INC-0417
- the Lyzr handover note
- the approved action whose receipt proved the Swytchcode ticket and Slack legs

## E. What can break the live app, and who owns it

Nothing clicked inside the console can break it: every write is appended to a
hash-chained ledger and nothing can be edited or deleted from a screen. What
can break it lives outside:

| Change | Who |
|---|---|
| anything in the Render dashboard (env vars, secret files, env groups) | Danish only |
| a push to `build/stage-1` while Auto-Deploy is on | anyone with repo write; keep Auto-Deploy **off** around the demo |
| removing the Swytchcode app from the Slack channel | do not |
| unpublishing or renaming the n8n workflow's webhook path | Hritik, do not |
| editing or deleting a Lyzr Studio agent | do not |
