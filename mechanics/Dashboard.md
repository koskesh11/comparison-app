# Dashboard

Needs the Dataview community plugin.

```dataview
TABLE type, status, pob_refs
FROM "Rules" OR "Models" OR "Scenarios" OR "Gaps" OR "Inbox"
SORT status ASC, file.mtime DESC
```
