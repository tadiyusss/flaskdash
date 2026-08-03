const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const themesDir = path.join(__dirname, "themes");
const installedTheme = path.join(__dirname, "core", "static", "css", "themes");

const args = process.argv.slice(2);

const watch = args.includes("--watch");
const minify = args.includes("--minify");

for (const theme of fs.readdirSync(themesDir)) {

    const themePath = path.join(themesDir, theme);

    if (!fs.statSync(themePath).isDirectory())
        continue;

    const input = path.join(themePath, "input.css");
    const output = path.join(installedTheme, theme + ".css");
    console.log(output)
    if (!fs.existsSync(input))
        continue;

    const cliArgs = [
        "-i",
        input,
        "-o",
        output
    ];

    if (watch)
        cliArgs.push("--watch");

    if (minify)
        cliArgs.push("--minify");

    console.log(`Building theme: ${theme}`);

    spawn(
        "tailwindcss",
        cliArgs,
        {
            stdio: "inherit",
            shell: true
        }
    );
}