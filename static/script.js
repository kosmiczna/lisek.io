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

function updateClock() {
    const now = new Date();
    const hour = +now.toLocaleString("en-GB", { timeZone: TIMEZONE, hour: "2-digit", hour12: false });
    const status = guessStatus(hour);

    document.getElementById("clock").textContent = now.toLocaleTimeString("en-GB", { timeZone: TIMEZONE });
    document.getElementById("status-text").textContent = status;

    // dot colour
    const dot = document.getElementById("dot");
    dot.classList.toggle("asleep", status === "probably asleep");
    dot.classList.toggle("unsure", status.startsWith("maybe"));
}

updateClock();
setInterval(updateClock, 1000);

// twitter emoji flage thing
function flagUrl(countryCode) {
    const codepoints = [...countryCode.toUpperCase()]
        .map(letter => (0x1F1E6 + letter.charCodeAt(0) - 65).toString(16));
    return "https://cdn.jsdelivr.net/gh/jdecked/twemoji@16.0.1/assets/svg/" + codepoints.join("-") + ".svg";
}

// scoresaber card
fetch("/api/scoresaber")
    .then(res => res.json())
    .then(data => {
        const nameColor = data.playerNameInGame.match(/#[0-9A-Fa-f]{6}/)[0];
        const headset = data.stats.device.hmd

        document.getElementById("ss-avatar").src = data.avatar;
        document.getElementById("ss-name").textContent = data.name;
        document.getElementById("ss-name").style.color = nameColor;
        document.getElementById("ss-flag").src = flagUrl(data.country);
        document.getElementById("ss-country-text").textContent = data.country + (headset ? " · " + headset : "");
        document.getElementById("ss-rank").textContent = "#" + data.stats.rank.toLocaleString();
        document.getElementById("ss-country-rank").textContent = "#" + data.stats.countryRank.toLocaleString();
        document.getElementById("ss-pp").textContent = Math.round(data.stats.totalPP).toLocaleString() + "pp";
        document.getElementById("ss-acc").textContent = data.stats.averageAccuracy.toFixed(1) + "%";
        document.getElementById("ss-plays").textContent = data.stats.totalSubmittedPlays.toLocaleString();
    });
