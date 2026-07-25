param(
    [string]$GitHubUser = 'Johnny2002Jab',
    [string]$RemoteRepo = 'https://github.com/Johnny2002Jab/Task-Tracker',
    [string]$CommitMessage = 'Initial commit: add full project',
    [switch]$ForcePush = $false
)

function Check-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "Git is not installed or not on PATH. Install Git (https://git-scm.com) or use winget: 'winget install --id Git.Git -e --source winget' and re-open PowerShell."
        exit 1
    }
}

function Ensure-GitIgnore {
    $gitignore = Join-Path $PWD '.gitignore'
    if (-not (Test-Path $gitignore)) {
        @"
venv/
.env
__pycache__/
.pytest_cache/
*.pyc
.DS_Store
node_modules/
"@ | Out-File -FilePath $gitignore -Encoding UTF8 -Force
        Write-Host "Created .gitignore"
    }
}

function Init-And-Push {
    Check-Git

    Ensure-GitIgnore

    if (-not (Test-Path '.git')) {
        git init
        Write-Host "Initialized local git repository"
    } else {
        Write-Host "Repository already initialized"
    }

    git config user.name "$env:USERNAME" 2>$null
    git config user.email "$env:USERNAME@example.com" 2>$null

    git add .
    # Try to commit; if commit fails (e.g., nothing to commit), continue gracefully
    git commit -m "$CommitMessage" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Nothing to commit or commit failed"
    }

    if ($RemoteRepo -ne '') {
        # If remote exists, try to set or update it
        if ((git remote) -match 'origin') {
            Write-Host "Remote 'origin' already exists. Updating URL to $RemoteRepo"
            git remote set-url origin $RemoteRepo
        } else {
            git remote add origin $RemoteRepo
            Write-Host "Added remote origin -> $RemoteRepo"
        }
    } elseif ($GitHubUser -ne '') {
        $Remote = "https://github.com/$GitHubUser/task-tracker.git"
        if ((git remote) -match 'origin') {
            Write-Host "Remote 'origin' already exists. Updating URL to $Remote"
            git remote set-url origin $Remote
        } else {
            git remote add origin $Remote
            Write-Host "Added remote origin -> $Remote"
        }
    } else {
        Write-Host "No remote configured. Provide -GitHubUser or -RemoteRepo to set remote and push."
        return
    }

    # Ensure main branch
    git branch -M main 2>$null

    if ($ForcePush.IsPresent) {
        git push -u origin main --force
    } else {
        git push -u origin main
    }
}

Init-And-Push
