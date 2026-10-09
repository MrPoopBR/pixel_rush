$ErrorActionPreference = 'Stop'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git não está instalado. Instale Git for Windows ou use GitHub Desktop.'
}

$remote = Read-Host 'Cole a URL HTTPS do repositório público vazio (ex.: https://github.com/USUARIO/pixel-rush-android.git)'
if ([string]::IsNullOrWhiteSpace($remote) -or $remote -notmatch '^https://github\.com/[^/]+/[^/]+(?:\.git)?$') {
    throw 'URL inválida. Use a URL HTTPS de um repositório no GitHub.'
}

if (-not (Test-Path '.git')) {
    git init
}
git branch -M main
git add .

$staged = git status --short
Write-Host "Arquivos staged:" -ForegroundColor Cyan
Write-Host $staged
Write-Host 'Confirme que nenhum .jks, keystore, senha ou token aparece acima.' -ForegroundColor Yellow
$confirm = Read-Host 'Digite PUBLICAR para continuar'
if ($confirm -cne 'PUBLICAR') { throw 'Publicação cancelada.' }

git config user.name (Read-Host 'Nome para este commit')
git config user.email (Read-Host 'E-mail para este commit')
git commit -m 'Initial Pixel Rush Android build setup'
if ((git remote) -contains 'origin') {
    git remote set-url origin $remote
} else {
    git remote add origin $remote
}
git push -u origin main
Write-Host 'Repositório publicado. Configure os quatro secrets descritos no README.' -ForegroundColor Green
