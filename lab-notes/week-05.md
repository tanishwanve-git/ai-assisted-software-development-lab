What I built — Cloned team repo, made my own branch, edited members.md, hit a conflict when Kushal merged first, resolved it by keeping both entries.

AI as tutor — Asked about the right order of fetch → merge, ran the commands myself.

What I figured out — After pushing my branch add-tanishwanve with my entry in members.md, I found that a teammate had already gotten their PR merged into main before mine. GitHub flagged my PR as conflicting because we had both edited the same lines in the same file. I ran git fetch origin to update my local view of the remote, then git merge origin/main on my branch to bring in the latest changes. That triggered the conflict — Git inserted the standard markers (<<<<<<<, =======, >>>>>>>) into members.md to show exactly where the two versions disagreed. Once I understood what those markers meant — that Git was simply asking me to decide which content to keep — the resolution was straightforward. I removed the markers, kept both entries in the file, and saved. From there it was git add members.md, git commit, and git push. The PR cleared immediately. The conflict itself was not complicated; what mattered was understanding that Git had not made an error — it had stopped and handed the decision back to me, which is exactly what it is supposed to do.
Verified — PR on GitHub showed no conflict markers and "able to merge."

Still don't understand — rebase vs merge in practice, and why --force-with-lease is needed after a rebase.
