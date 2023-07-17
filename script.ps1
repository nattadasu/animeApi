Import-Module ./stringToSlug.psm1

./silverYashaGenerate.ps1

Invoke-WebRequest -Method Get -Uri "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json" -OutFile ./aod.json

"Updated on $(Get-Date)" | Out-File ./updated -Force -Encoding utf8

if ((git diff ./aod.json) -or (git diff ./syRelation.json)) {
	Write-Host "AOD and/or SilverYasha have been updated"
}
else {
	Write-Host "AOD and SilverYasha are up to date"
	#force exit
	exit
}

Write-Host "[$(Get-Date)] Loading JSON"
$json = Get-Content -Path ./aod.json -Raw | ConvertFrom-Json
$syJson = Get-Content -Path ./syRelation.json | ConvertFrom-Json

$nmUri = "https://notify.moe/anime/"
$malUri = "https://myanimelist.net/anime/"
$lcUri = "https://livechart.me/anime/"
$kiUri = "https://kitsu.io/anime/"
$asUri = "https://anisearch.com/anime/"
$apUri = "https://anime-planet.com/anime/"
$alUri = "https://anilist.co/anime/"
$adbUri = "https://anidb.net/anime/"

$services = @(
	"anidb",
	"anilist",
	"animeplanet",
	"anisearch",
	"kaize",
	"kitsu",
	"livechart",
	"myanimelist",
	"notify",
	"silveryasha"
)

foreach ($dir in $services) {
	# Cleanup directory
	Remove-Item "./$($dir)" -Force -Recurse -Confirm:$False
	# Create new dir
	New-Item -ItemType Directory -Path $dir -Force
}

Write-Host ""

$aniDb = [ordered]@{}; $aniList = [ordered]@{}; $animePlanet = [ordered]@{}; $aniSearch = [ordered]@{}; $kaize = [ordered]@{}; $kitsu = [ordered]@{}; $liveChart = [ordered]@{}; $mal = [ordered]@{}; $notify = [ordered]@{}; $silverYasha = [ordered]@{}; $index = @()
$aniDbArr = @(); $aniListArr = @(); $animePlanetArr = @(); $aniSearchArr = @(); $kaizeArr = @(); $kitsuArr = @(); $liveChartArr = @(); $malArr = @(); $notifyArr = @(); $silverYashaArr = @()
$n = 1
$total = $json.data.Count
foreach ($data in $json.data) {
	Write-Host "`r[$(Get-Date)] [$($n)/$($total)] Writing: $($data.title)" -NoNewLine
	$adbId = $Null; $alId = $Null; $apId = $Null; $asId = $Null; $kiId = $Null; $kzId = $Null; $lcId = $Null; $malId = $Null; $nmId = $Null; $syId = $Null
	foreach ($url in $data.sources) {
		if ($url -match $adbUri) { $adbId = $url.Replace($adbUri, '') }
		elseif ($url -match $alUri) { $alId = $url.Replace($alUri, '') }
		elseif ($url -match $apUri) { $apId = $url.Replace($apUri, '') }
		elseif ($url -match $asUri) { $asId = $url.Replace($asUri, '') }
		elseif ($url -match $kiUri) { $kiId = $url.Replace($kiUri, '') }
		elseif ($url -match $lcUri) { $lcId = $url.Replace($lcUri, '') }
		elseif ($url -match $malUri) { $malId = $url.Replace($malUri, '') }
		elseif ($url -match $nmUri) { $nmId = $url.Replace($nmUri, '') }
	}

	$titleFix = $data.title -Replace '-', ' ' -Replace 'Ψ', 'ps' -Replace "'", '' -Replace "_", " " -Replace '@', ' at '
	# $forbidden = @(
		# "'",
		# '☆'
	# )
	# foreach ($kinshi in $forbidden) {
		# $titleFix = $titleFix -Replace $kinshi, ''
	# }
	$titleFix = $titleFix -Replace '   ', ' ' -Replace 'at $', 'at'

	# Kaize uses MAL Title rules for its media title and slug
	if ($Null -ne $malId) {
		$kzId = switch ($data.title) {
			"Arifureta Shokugyou de Sekai Saikyou: Arifureta Yorimachi de Sekai Saikyou" { "arifureta-shokugyou-de-sekai-saikyou-2nd-season-special" }
			"21 Emon" { "21-emon-1" }
			"3x3 Eyes: Seima Densetsu" { "3x3-eyes-seima-densetsu-1" }
			"Akiba Meido Sensou" { "akiba-maid-sensou" }
			"Ali Baba Dadao Qibing" { "alibaba-dadao-qibing" }
			"Ali Baba Yu Shen Deng" { "alibaba-yu-shen-deng" }
			"Ba Bu Xiongmao" { "babo-xiongmao" }
			"Bakumatsu: Crisis" { "bakumatsu-crisis-1" }
			"Boruto: Naruto the Movie - Naruto ga Hokage ni Natta Hi" { "boruto-naruto-the-movie-naruto-ga-hokage-ni-natta-hi-1" }
			"Digimon Adventure:" { "digimon-adventure-2" }
			"Dog Days''" { "dog-days-2" }
			"Dog Days'" { "dog-days-1" }
			"Duel Masters!!" { "duel-masters-2" }
			"Duel Masters!" { "duel-masters-1" }
			"Fella Pure: Mitarashi-san Chi no Jijou The Animation" { "fella-pure-mitarashi-san-chi-no-jijou-the-animation-1" }
			"Gintama." { "gintama-2" }
			"Gintama'" { "gintama-1" }
			"Gintama°" { "gintama-3" }
			"Gundam Build Fighters: Battlogue" { "gundam-build-fighters-battlogue-1" }
			"Hataraku Saibou!! Saikyou no Teki, Futatabi. Karada no Naka wa `"Chou`" Oosawagi!" { "hataraku-saibou-saikyou-no-teki-futatabi-karada-no-naka-wa-chou-oosawagi-1" }
			"Himawari!!" { "himawari-2" }
			"Himawari!" { "himawari-1" }
			"Inu x Boku SS Special" { "inu-x-boku-ss-miketsukami-kunhenkaswitchomamagoto" }
			"Lian Qi Lianle 300 Nian" { "lianqi-lianle-3000-nian" }
			"Motto To LOVE-Ru" { "motto-to-love-ru-1" }
			"Qiubite Da Nao Shi Er Xingzuo" { "cupid-da-nao-shi-er-xingzuo" }
			"Shinryaku!! Ika Musume" { "shinryaku-ika-musume-2" }
			"Shinryaku!? Ika Musume" { "shinryaku-ika-musume-1" }
			"To LOVE-Ru" { "to-love-ru-1" }
			"Ura Sekai Picnic" { "urasekai-picnic" }
			"Working!!!" { "working-1" }
			"Working'!!" { "working-2" }
			"Youkai Watch ♪" { "youkai-watch-1" }
			"Youkai Watch!" { "youkai-watch-2" }
			"Yuru Yuri♪♪" { "yuru-yuri-1" }
			"Yuru Yuri," { "yuru-yuri-2" }
			# Bypass Invalid name
			"◯" { "-1" }
			"∞" { "-2" }
			"アタシは問題作" { "-3" }
			Default { ConvertTo-Slug -Text $titleFix -Delimiter '-' }
		}
		if (($kaize.$kzId -match '-[\d]+$') -and ($data.title -notmatch ' [\d]+$')) {
			[int]$enum = $Matches[0] -Replace '-', ''
			$kzId = $kzId -Replace $Matches[0], ''
			$kzId = "$($kzId)-$($enum + 1)"
		}
		elseif ($kaize.$kzId) {
			$kzId = "$($kzId)-1"
		}
	}

	# Add Silver Yasha Relation
	if ($Null -ne $malId) {
		[string]$syMalId = $malId
		if ($syJson.$syMalId) {
			$syId = $syJson.$malId.silverYashaId
		}
		else {
			$syId = $Null
		}
	}
	
	$title = $data.title

	$entryData = [ordered]@{
		title       = [string]$title
		aniDb       = if ($Null -ne $adbId) { [int]$adbId } else { $Null }
		aniList     = if ($Null -ne $alId) { [int]$alId } else { $Null }
		animePlanet = if ($Null -ne $apId) { [string]$apId } else { $Null }
		aniSearch   = if ($Null -ne $asId) { [int]$asId } else { $Null }
		kaize       = if ($Null -ne $kzId) { [string]$kzId } else { $Null }
		kitsu       = if ($Null -ne $kiId) { [int]$kiId } else { $Null }
		liveChart   = if ($Null -ne $lcId) { [int]$lcId } else { $Null }
		myAnimeList = if ($Null -ne $malId) { [int]$malId } else { $Null }
		notifyMoe   = if ($Null -ne $nmId) { [string]$nmId } else { $Null }
		silverYasha = if ($Null -ne $syId) { [int]$syId } else { $Null }
	}

	$index += [PSCustomObject]$entryData

	# start building databases
	if ($Null -ne $apId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./animeplanet/$apId -Encoding utf8 -Force
		$animePlanet += @{
			"$($apId)" = $entryData
		}
		$animePlanetArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $malId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./myanimelist/$malId -Encoding utf8 -Force
		$mal += @{
			"$($malId)" = $entryData
		}
		$malArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $kzId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./kaize/$kzId -Encoding utf8 -Force
		$kaize += @{
			"$($kzId)" = $entryData
		}
		$kaizeArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $lcId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./livechart/$lcId -Encoding utf8 -Force
		$liveChart += @{
			"$($lcId)" = $entryData
		}
		$liveChartArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $nmId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./notify/$nmId -Encoding utf8 -Force
		$notify += @{
			"$($nmId)" = $entryData
		}
		$notifyArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $kiId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./kitsu/$kiId -Encoding utf8 -Force
		$kitsu += @{
			"$($kiId)" = $entryData
		}
		$kitsuArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $asId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./anisearch/$asId -Encoding utf8 -Force
		$aniSearch += @{
			"$($asId)" = $entryData
		}
		$aniSearchArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $alId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./anilist/$alId -Encoding utf8 -Force
		$aniList += @{
			"$($alId)" = $entryData
		}
		$aniListArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $adbId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./anidb/$adbId -Encoding utf8 -Force
		$aniDb += @{
			"$($adbId)" = $entryData
		}
		$aniDbArr += [PSCustomObject]$entryData
	}
	if ($Null -ne $syId) {
		$entryData | ConvertTo-Json -Depth 99 | Out-File ./silveryasha/$syid -Encoding utf8 -Force
		$silverYasha += @{
			"$($syId)" = $entryData
		}
		$silverYashaArr += [PSCustomObject]$entryData
	}
	$n++
}


Write-Host "`n`n[$(Get-Date)] Exporting AniDB"
$aniDb | ConvertTo-Json -Depth 99 | Out-File ./anidb.json -Encoding utf8 -Force
$aniDbArr | ConvertTo-Json -Depth 99 | Out-File './anidb().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting AniList"
$aniList | ConvertTo-Json -Depth 99 | Out-File ./anilist.json -Encoding utf8 -Force
$aniListArr | ConvertTo-Json -Depth 99 | Out-File './anilist().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting Anime-Planet"
$aniPlanet | ConvertTo-Json -Depth 99 | Out-File ./animeplanet.json -Encoding utf8 -Force
$animePlanetArr | ConvertTo-Json -Depth 99 | Out-File './animeplanet().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting AniSearch"
$aniSearch | ConvertTo-Json -Depth 99 | Out-File ./anisearch.json -Encoding utf8 -Force
$aniSearchArr | ConvertTo-Json -Depth 99 | Out-File './anisearch().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting Kaize"
$kaize | ConvertTo-Json -Depth 99 | Out-File ./kaize.json -Encoding utf8 -Force
$kaizeArr | ConvertTo-Json -Depth 99 | Out-File './kaize().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting Kitsu"
$kitsu | ConvertTo-Json -Depth 99 | Out-File ./kitsu.json -Encoding utf8 -Force
$kitsuArr | ConvertTo-Json -Depth 99 | Out-File './kitsu().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting LiveChart"
$liveChart | ConvertTo-Json -Depth 99 | Out-File ./livechart.json -Encoding utf8 -Force
$liveChartArr | ConvertTo-Json -Depth 99 | Out-File './livechart().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting MAL"
$mal | ConvertTo-Json -Depth 99 | Out-File ./myanimelist.json -Encoding utf8 -Force
$malArr | ConvertTo-Json -Depth 99 | Out-File './myanimelist().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting Notify.moe"
$notify | ConvertTo-Json -Depth 99 | Out-File ./notify.json -Encoding utf8 -Force
$notifyArr | ConvertTo-Json -Depth 99 | Out-File './notify().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Exporting Silver Yasha"
$silverYasha | ConvertTo-Json -Depth 99 | Out-File ./silverYasha.json -Encoding utf8 -Force
$silverYashaArr | ConvertTo-Json -Depth 99 | Out-File './silverYasha().json' -Encoding utf8 -Force

Write-Host "[$(Get-Date)] Export to index"
$index | ConvertTo-Json -Depth 99 | Out-File ./index.json -Encoding utf8 -Force
