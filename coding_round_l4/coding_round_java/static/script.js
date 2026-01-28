// ===========================================================
// DOM ELEMENTS
// ===========================================================
const editor = document.getElementById("editor");
const outputBox = document.getElementById("output-box");
const sampleContainer = document.getElementById("sample-tests");
const runBtn = document.getElementById("run-btn");
const runHiddenBtn = document.getElementById("run-hidden-btn");
const submitBtn = document.getElementById("submit-btn");
const timerDisplay = document.getElementById("timer-display");
const scoreDisplay = document.getElementById("score-display");
const violationDisplay = document.getElementById("violation-display");

// ===========================================================
// CONSTANTS & STORAGE KEYS
// ===========================================================
const TOTAL_TIME_SECONDS = 30 * 60;

const STORAGE_KEYS = {
    START_TIME: "java_exam_start_time",
    FOCUS_COUNT: "java_focus_lost",
    CODE: "java_code"
};

// ===========================================================
// STATE FLAGS
// ===========================================================
let examFinished = false;
let isPageRefreshing = false;

// ===========================================================
// RESTORE STATE ON LOAD
// ===========================================================
let examStartTime = sessionStorage.getItem(STORAGE_KEYS.START_TIME);
if (!examStartTime) {
    examStartTime = Date.now();
    sessionStorage.setItem(STORAGE_KEYS.START_TIME, examStartTime);
} else {
    examStartTime = parseInt(examStartTime, 10);
}

let tabViolations = parseInt(
    sessionStorage.getItem(STORAGE_KEYS.FOCUS_COUNT) || "0",
    10
);

violationDisplay.textContent =
    tabViolations > 0 ? `Focus lost ${tabViolations} time(s)` : "Focus OK";

// restore editor code
const savedCode = sessionStorage.getItem(STORAGE_KEYS.CODE);
editor.value = savedCode ? savedCode : STARTER;

// ===========================================================
// SAMPLE TESTS (LEFT PANEL)
// ===========================================================
sampleContainer.innerHTML = "";

if (QUESTION && Array.isArray(QUESTION.public_tests)) {
    QUESTION.public_tests.forEach((t, idx) => {
        const div = document.createElement("div");
        div.className = "sample-block";
        div.innerHTML = `
            <div><strong>Example ${idx + 1}</strong></div>
            <div><strong>Input:</strong> <code>${JSON.stringify(t.input)}</code></div>
            <div><strong>Expected:</strong> <code>${JSON.stringify(t.expected)}</code></div>
        `;
        sampleContainer.appendChild(div);
    });
}

// ===========================================================
// OUTPUT HELPERS
// ===========================================================
function setOutput(msg) {
    outputBox.textContent = msg;
    outputBox.scrollTop = outputBox.scrollHeight;
}

function appendOutput(msg) {
    outputBox.textContent += "\n" + msg;
    outputBox.scrollTop = outputBox.scrollHeight;
}

// ===========================================================
// TIMER LOGIC
// ===========================================================
function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
}

function computeTimeLeft() {
    const elapsed = Math.floor((Date.now() - examStartTime) / 1000);
    return Math.max(TOTAL_TIME_SECONDS - elapsed, 0);
}

let timeLeft = computeTimeLeft();
timerDisplay.textContent = formatTime(timeLeft);
if (timeLeft <= 60) {
    timerDisplay.style.color = "#ff5555";
}


const timerId = setInterval(() => {
    if (examFinished) return;

    timeLeft = computeTimeLeft();
    timerDisplay.textContent = formatTime(timeLeft);

    if (timeLeft <= 60) timerDisplay.style.color = "#ff5555";

    if (timeLeft <= 0) {
        setOutput("\n⏳ Time is up! Auto-submitting...");
        submitTest();
        clearInterval(timerId);
    }
}, 1000);

// ===========================================================
// REFRESH & TAB SWITCH DETECTION
// ===========================================================
window.addEventListener("beforeunload", () => {
    isPageRefreshing = true;
});

document.addEventListener("visibilitychange", () => {
    if (!examFinished && document.hidden && !isPageRefreshing) {
        tabViolations++;
        sessionStorage.setItem(STORAGE_KEYS.FOCUS_COUNT, tabViolations);
        violationDisplay.textContent = `Focus lost ${tabViolations} time(s)`;
        appendOutput(`[Proctor] Focus lost #${tabViolations}`);
    }
});

// persist code
editor.addEventListener("input", () => {
    sessionStorage.setItem(STORAGE_KEYS.CODE, editor.value);
});

// ===========================================================
// CORE API CALL
// ===========================================================
async function executeTests({ submit = false, runHidden = false }) {
    setOutput(
        submit
            ? "Submitting final solution..."
            : runHidden
            ? "Running hidden test cases..."
            : "Running public test cases..."
    );

    const response = await fetch("/run_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            code: editor.value,
            language: "java",
            submit,
            run_hidden: runHidden,
            focus_lost: tabViolations
        })
    });

    return response.json();
}

// ===========================================================
// TEST RESULTS RENDERER
// ===========================================================
function appendTestResults(testResults) {
    if (!Array.isArray(testResults)) return;

    appendOutput("\n📋 Test Case Details:\n");

    testResults.forEach(tc => {
        appendOutput(
            `${tc.passed ? "✅" : "❌"} Test Case ${tc.index} (${tc.visibility})`
        );
        appendOutput(`Input: ${JSON.stringify(tc.input)}`);
        appendOutput(`Expected: ${tc.expected}`);
        appendOutput(`Actual: ${tc.actual}\n`);
    });
}

// ===========================================================
// BUTTON ACTIONS
// ===========================================================
async function runPublicTests() {
    const result = await executeTests({});

    // 🔥 ADD THIS CHECK
    if (result.error) {
        setOutput("❌ Error:\n\n" + result.message);
        scoreDisplay.textContent = "Score: 0/0";
        return;
    }

    scoreDisplay.textContent = `Score: ${result.passed}/${result.total}`;
    setOutput(`✅ Public Tests Passed: ${result.passed}/${result.total}`);
    appendTestResults(
        result.test_results.filter(t => t.visibility === "public")
    );
}


async function runHiddenTests() {
    const result = await executeTests({ runHidden: true });

    // 🔥 ADD THIS CHECK
    if (result.error) {
        setOutput("❌ Error:\n\n" + result.message);
        scoreDisplay.textContent = "Hidden: 0/0";
        return;
    }

    scoreDisplay.textContent = `Hidden: ${result.passed}/${result.total}`;
    setOutput(`🔒 Hidden Tests Passed: ${result.passed}/${result.total}`);
    appendTestResults(result.test_results);
}


async function submitTest() {
    examFinished = true;

    runBtn.disabled = true;
    runHiddenBtn.disabled = true;
    submitBtn.disabled = true;
    editor.disabled = true;

    const result = await executeTests({ submit: true });

    // 🔥 ADD THIS CHECK
    if (result.error) {
        setOutput("❌ Error during submission:\n\n" + result.message);
        return;
    }

    scoreDisplay.textContent = `Final Score: ${result.passed}/${result.total}`;
    setOutput("✅ Test submitted successfully.\n\nYou may now close this page.");

    sessionStorage.removeItem(STORAGE_KEYS.START_TIME);
    sessionStorage.removeItem(STORAGE_KEYS.FOCUS_COUNT);
    sessionStorage.removeItem(STORAGE_KEYS.CODE);

}

// ===========================================================
// EVENT BINDINGS
// ===========================================================
runBtn.addEventListener("click", runPublicTests);
runHiddenBtn.addEventListener("click", runHiddenTests);
submitBtn.addEventListener("click", submitTest);

