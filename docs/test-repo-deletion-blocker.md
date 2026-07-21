# Blocker: cannot delete accidental test repo via API

Repository: `MrFaDeveloper/Google-Weather-Open-API` (empty test name with hyphens).

## Attempt

```bash
gh api -X DELETE /repos/MrFaDeveloper/Google-Weather-Open-API
gh repo delete MrFaDeveloper/Google-Weather-Open-API --yes
```

## Result

```text
HTTP 403: Must have admin rights to Repository.
This API operation needs the "delete_repo" scope.
Token scopes present: gist, read:org, repo
```

`gh auth refresh -s delete_repo` requires interactive browser auth and cannot be completed non-interactively in this agent session.

## Mitigation in place

Remote README on the test repo states **Deprecated** and redirects to:

https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI

Owner can delete after:

```bash
gh auth refresh -h github.com -s delete_repo
gh repo delete MrFaDeveloper/Google-Weather-Open-API --yes
```
