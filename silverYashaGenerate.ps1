$silverYashaPath = './silverYashaDb.json'
$silverYashaLink = 'https://db.silveryasha.web.id/ajax/anime/dtanime'
try {
	Invoke-WebRequest -Method Get -Uri $silverYashaLink -OutFile $silverYashaPath
}
catch {
	Write-Error -Message "Unfortunately we can not bypass the freaking cloudflare bruh" -ErrorAction continue
}

$json = Get-Content -Path $silverYashaPath -Raw | ConvertFrom-Json
$total = $json.data.Count

$index = [ordered]@{}; $n = 1
foreach ($entry in $json.data) {
	Write-Host "`r[$($n)/$($total)] Converting $($entry.title) ($($entry.id))" -NoNewLine
	$index += [ordered]@{
		"$($entry.mal_id)" = [ordered]@{
			title = $entry.title
			titleAlt = Switch ($entry.title_alt) { '' { $null } Default { $entry.title_alt } }
			silverYashaId = $entry.id
		}
	}
	$n++
}

$index | ConvertTo-Json -Depth 99 | Out-File ./syRelation.json
# Remove-Item $silverYashaPath
