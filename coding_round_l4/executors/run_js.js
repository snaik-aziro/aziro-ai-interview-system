// executors/run_js.js
const fs = require("fs");

let input = "";

// Read ALL stdin
process.stdin.on("data", chunk => {
    input += chunk;
});

process.stdin.on("end", () => {
    try {
        const payload = JSON.parse(input);
        const code = payload.code;
        const args = payload.args || [];

        // Wrap candidate code safely
        const wrappedCode = `
${code}

let __result;
try {
    __result = solve(...${JSON.stringify(args)});
} catch (e) {
    console.error(e.toString());
    process.exit(2);
}

if (__result !== undefined) {
    if (typeof __result === "object") {
        console.log(JSON.stringify(__result));
    } else {
        console.log(__result);
    }
}
`;

        // Write temp file
        fs.writeFileSync("solution.js", wrappedCode);

        // Execute
        const { execSync } = require("child_process");
        const output = execSync("node solution.js", {
            timeout: 5000,
            encoding: "utf-8"
        });

        // SUCCESS
        console.log(JSON.stringify({
            stdout: output.trim(),
            stderr: "",
            returncode: 0
        }));

    } catch (err) {
        console.log(JSON.stringify({
            stdout: "",
            stderr: err.toString(),
            returncode: 1
        }));
    }
});
