"use strict";

const fs = require("node:fs");
const path = require("node:path");
const {
	spawn
} = require("node:child_process");

const ROOT = __dirname;
const THEMES_DIR = path.join(ROOT, "themes");
const EXTENSIONS_DIR = path.join(ROOT, "extensions");
const OUTPUT_ROOT = path.join(ROOT, "core", "static", "css", "themes");
const INPUT_FILE = "input.css";
const IS_WINDOWS = process.platform === "win32";

const SAFE_NAME = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;
const CLI_PACKAGES = ["@tailwindcss/cli", "tailwindcss"];

const FLAGS = new Map([
	["--watch", "watch"],
	["--minify", "minify"],
	["--help", "help"],
]);

function parseArgs(argv) {
	const options = {
		watch: false,
		minify: false,
		help: false
	};

	for (const arg of argv) {
		const key = FLAGS.get(arg);
		if (!key) {
			throw new Error(`Unknown argument: ${arg}`);
		}
		options[key] = true;
	}

	return options;
}

function printUsage() {
	console.log("Usage: node build-themes.js [--watch] [--minify] [--help]");
}

function listSubdirectories(dir) {
	if (!fs.existsSync(dir)) {
		return [];
	}

	return fs
		.readdirSync(dir, {
			withFileTypes: true
		})
		.filter((entry) => entry.isDirectory() && SAFE_NAME.test(entry.name))
		.map((entry) => entry.name)
		.sort();
}

function isFile(filePath) {
	try {
		return fs.statSync(filePath).isFile();
	} catch {
		return false;
	}
}

function assertInside(base, target) {
	const relative = path.relative(base, target);
	if (relative.startsWith("..") || path.isAbsolute(relative)) {
		throw new Error(`Path escapes its base directory: ${target}`);
	}
}

function pathKey(filePath) {
	const normalized = path.normalize(filePath);
	return IS_WINDOWS ? normalized.toLowerCase() : normalized;
}

function discoverTargets() {
	const targets = [];

	for (const theme of listSubdirectories(THEMES_DIR)) {
		targets.push({
			label: theme,
			input: path.join(THEMES_DIR, theme, INPUT_FILE),
			output: path.join(OUTPUT_ROOT, `${theme}.css`),
		});
	}

	for (const extension of listSubdirectories(EXTENSIONS_DIR)) {
		const extensionThemes = path.join(EXTENSIONS_DIR, extension, "themes");

		for (const theme of listSubdirectories(extensionThemes)) {
			targets.push({
				label: `${extension}/${theme}`,
				input: path.join(extensionThemes, theme, INPUT_FILE),
				output: path.join(OUTPUT_ROOT, `${theme}.css`),
			});
		}
	}

	const seen = new Set();

	return targets.filter((target) => {
		if (!isFile(target.input)) {
			return false;
		}
		assertInside(OUTPUT_ROOT, target.output);

		const key = pathKey(target.output);
		if (seen.has(key)) {
			throw new Error(`Two themes write to the same file: ${target.output}`);
		}
		seen.add(key);
		return true;
	});
}

function resolveTailwindCli() {
	for (const pkg of CLI_PACKAGES) {
		const pkgDir = path.join(ROOT, "node_modules", ...pkg.split("/"));
		const manifestPath = path.join(pkgDir, "package.json");

		if (!isFile(manifestPath)) {
			continue;
		}

		const {
			bin
		} = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
		const entry = typeof bin === "string" ? bin : bin && bin.tailwindcss;

		if (entry) {
			return path.resolve(pkgDir, entry);
		}
	}

	throw new Error(
		"Tailwind CLI not found. Install it with: npm install -D tailwindcss @tailwindcss/cli"
	);
}

const children = new Set();

function runBuild(cliPath, target, options) {
	fs.mkdirSync(path.dirname(target.output), {
		recursive: true
	});

	const args = [cliPath, "-i", target.input, "-o", target.output];
	if (options.watch) args.push("--watch");
	if (options.minify) args.push("--minify");

	console.log(`Building theme: ${target.label}`);

	return new Promise((resolve) => {
		const child = spawn(process.execPath, args, {
			stdio: "inherit",
			windowsHide: true,
		});
		children.add(child);

		child.on("error", (error) => {
			children.delete(child);
			console.error(`[${target.label}] failed to start: ${error.message}`);
			resolve(1);
		});

		child.on("close", (code, signal) => {
			children.delete(child);
			const failed = code !== 0 && !signal;
			if (failed) {
				console.error(`[${target.label}] exited with code ${code}`);
			}
			resolve(failed ? code ?? 1 : 0);
		});
	});
}

function stopChildrenOnSignal() {
	for (const signal of ["SIGINT", "SIGTERM"]) {
		process.on(signal, () => {
			for (const child of children) {
				child.kill();
			}
		});
	}
}

async function main() {
	const options = parseArgs(process.argv.slice(2));

	if (options.help) {
		printUsage();
		return 0;
	}

	const targets = discoverTargets();
	if (targets.length === 0) {
		console.warn(`No themes found (looked for ${INPUT_FILE} files).`);
		return 0;
	}

	const cliPath = resolveTailwindCli();
	stopChildrenOnSignal();

	const codes = await Promise.all(
		targets.map((target) => runBuild(cliPath, target, options))
	);

	const failures = codes.filter((code) => code !== 0).length;
	if (failures > 0) {
		console.error(`${failures} of ${targets.length} theme builds failed.`);
		return 1;
	}

	if (!options.watch) {
		console.log(`Built ${targets.length} theme(s).`);
	}
	return 0;
}

main().then(
	(code) => {
		process.exitCode = code;
	},
	(error) => {
		console.error(error.message);
		process.exitCode = 1;
	}
);