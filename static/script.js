const $ = id => document.getElementById(id);

const TIMEZONE = "Europe/London";

// sortof sleep schedule ish
function guessStatus(hour) {
    if (hour < 3) return "probably still awake";
    if (hour < 9) return "probably asleep";
    if (hour < 11) return "maybe awake";
    if (hour < 15) return "probably awake";
    if (hour < 17) return "maybe asleep";
    return "probably awake";
}

// cock
function updateClock() {
    const now = new Date();
    const hour = +now.toLocaleString("en-GB", { timeZone: TIMEZONE, hour: "2-digit", hour12: false });
    const status = guessStatus(hour);

    $("clock").textContent = now.toLocaleTimeString("en-GB", { timeZone: TIMEZONE });
    $("status-text").textContent = status;

    // dot colour
    $("dot").classList.toggle("asleep", status === "probably asleep");
    $("dot").classList.toggle("unsure", status.startsWith("maybe"));
}

updateClock();
setInterval(updateClock, 1000);

// twitter emoji flag thing
function flagUrl(countryCode) {
    const codepoints = [...countryCode.toUpperCase()]
        .map(letter => (0x1F1E6 + letter.charCodeAt(0) - 65).toString(16));
    return "https://cdn.jsdelivr.net/gh/jdecked/twemoji@16.0.1/assets/svg/" + codepoints.join("-") + ".svg";
}

// scoresaber card
fetch("/api/scoresaber")
    .then(res => res.json())
    .then(data => {
        const stats = data.stats;
        const nameColor = data.playerNameInGame.match(/#[0-9A-Fa-f]{6}/)[0];
        const headset = stats.device.hmd;

        $("ss-avatar").src = data.avatar;
        $("ss-name").textContent = data.name;
        $("ss-name").style.color = nameColor;
        $("ss-flag").src = flagUrl(data.country);
        $("ss-country-text").textContent = data.country + (headset ? " · " + headset : "");
        $("ss-rank").textContent = "#" + stats.rank.toLocaleString();
        $("ss-country-rank").textContent = "#" + stats.countryRank.toLocaleString();

        // improvemtn
        if (stats.rankChange) {
            $("ss-rank-change").textContent = (stats.rankChange > 0 ? "▲" : "▼") + Math.abs(stats.rankChange);
            $("ss-rank-change").classList.add(stats.rankChange > 0 ? "up" : "down");
        }
        $("ss-pp").textContent = Math.round(stats.totalPP).toLocaleString() + "pp";
        $("ss-acc").textContent = stats.averageAccuracy.toFixed(1) + "%";
        $("ss-plays").textContent = stats.totalSubmittedPlays.toLocaleString();
    });

// github contribution heatmap
fetch("/api/github")
    .then(res => res.json())
    .then(json => {
        const user = json.data.user;
        const days = user.contributionsCollection.contributionCalendar.weeks
            .flatMap(week => week.contributionDays)
            .map(day => ({ date: day.date, count: day.contributionCount }));

        // intensity calculator?
        const maxCount = Math.max(...days.map(day => day.count), 1);
        for (const day of days) {
            day.level = day.count === 0 ? 0 : Math.min(4, Math.ceil((day.count / maxCount) * 4));
        }

        // 6 monat
        let start = Math.max(0, days.length - 182);
        while (start > 0 && new Date(days[start].date).getDay() !== 0) start--;
        const shown = days.slice(start);
        const weeks = Math.ceil(shown.length / 7);

        const grid = $("contrib");
        grid.style.gridTemplateColumns = `repeat(${weeks}, 1fr)`;
        for (let weekday = 0; weekday < 7; weekday++) {
            for (let week = 0; week < weeks; week++) {
                const day = shown[week * 7 + weekday];
                const cell = document.createElement("i");
                if (!day) cell.className = "empty";
                else if (day.level) cell.className = "l" + day.level;
                if (day) cell.title = `${day.date}: ${day.count}`;
                grid.appendChild(cell);
            }
        }

        $("gh-total").textContent = shown.reduce((sum, day) => sum + day.count, 0).toLocaleString();
        $("gh-best").textContent = Math.max(...shown.map(day => day.count)).toLocaleString();
        $("gh-repos").textContent = user.repositories.totalCount;

        // duolingo streak
        let i = days.length - 1;
        if (days[i].count === 0) i--;
        let streak = 0;
        while (i >= 0 && days[i].count > 0) { streak++; i--; }
        $("gh-streak").textContent = streak + "d";
    });
