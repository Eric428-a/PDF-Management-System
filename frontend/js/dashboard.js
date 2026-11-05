
"use strict";

let currentJobId = null;
let isLoggingOut = false;


// --------------------------------------------------
// HELPERS
// --------------------------------------------------

const $ = (id) => document.getElementById(id);


function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, function(character) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[character];
    });
}


function showMessage(elementId, message, type = "info") {
    const element = $(elementId);

    if (!element) return;

    element.textContent = message;
    element.className = `message ${type}`;
}


async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (response.status === 401) {
        window.location.replace("/");
        throw new Error("Your session has expired. Please sign in again.");
    }

    if (!response.ok) {
        throw new Error(
            data.detail || data.message || "An unexpected error occurred."
        );
    }

    return data;
}


function formatStatus(status) {
    const labels = {
        uploaded: "Uploaded",
        completed: "Target achieved",
        completed_above_target: "Above target"
    };

    return labels[status] || status || "Unknown";
}


function formatBytes(kb) {
    if (
        kb === null ||
        kb === undefined ||
        !Number.isFinite(Number(kb))
    ) {
        return "-";
    }

    return `${Number(kb).toFixed(2)} KB`;
}


function formatNumber(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toLocaleString();
}


// --------------------------------------------------
// AUTHENTICATION
// --------------------------------------------------

async function loadCurrentUser() {
    try {
        const data = await apiRequest("/api/auth/me");

        const username = data.username || "Administrator";

        const usernameDisplay = $("usernameDisplay");

        if (usernameDisplay) {
            usernameDisplay.textContent = username;
        }

        const avatar = document.querySelector(".user-avatar");

        if (avatar) {
            avatar.textContent = username.charAt(0).toUpperCase();
        }

    } catch (error) {
        console.error("Could not load current user:", error);
    }
}


// LOGOUT

$("logoutButton").addEventListener("click", async function() {
    if (isLoggingOut) return;

    isLoggingOut = true;

    const button = $("logoutButton");

    button.disabled = true;
    button.textContent = "Signing out...";

    try {
        await apiRequest("/api/auth/logout", {
            method: "POST"
        });

        window.location.replace("/");

    } catch (error) {
        console.error("Logout failed:", error);

        alert(error.message || "Unable to sign out. Please try again.");

        isLoggingOut = false;

        button.disabled = false;
        button.textContent = "↪ Sign Out";
    }
});


// --------------------------------------------------
// DASHBOARD STATISTICS
// --------------------------------------------------

async function loadDashboardStats() {
    try {
        const data = await apiRequest("/api/dashboard/stats");

        $("totalFiles").textContent =
            formatNumber(data.total_files);

        $("compressedFiles").textContent =
            formatNumber(data.compressed_files);

        $("targetMet").textContent =
            formatNumber(data.target_met);

        $("savedMB").textContent =
            `${Number(data.saved_mb || 0).toFixed(2)} MB`;

    } catch (error) {
        console.error(
            "Could not load dashboard statistics:",
            error
        );
    }
}


// --------------------------------------------------
// FILE SELECTION
// --------------------------------------------------

$("pdfFile").addEventListener("change", function() {
    const file = this.files[0];

    $("selectedFileName").textContent = file
        ? file.name
        : "No file selected";

    if (file && !file.name.toLowerCase().endsWith(".pdf")) {
        showMessage(
            "uploadMessage",
            "Please select a PDF document.",
            "error"
        );
    } else {
        $("uploadMessage").textContent = "";
        $("uploadMessage").className = "message";
    }
});


// --------------------------------------------------
// PDF UPLOAD AND INSPECTION
// --------------------------------------------------

$("uploadForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const file = $("pdfFile").files[0];

    if (!file) {
        showMessage(
            "uploadMessage",
            "Please select a PDF file.",
            "error"
        );

        return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        showMessage(
            "uploadMessage",
            "Only PDF files are supported.",
            "error"
        );

        return;
    }

    const targetKB = Number($("targetKB").value);

    if (
        !Number.isInteger(targetKB) ||
        targetKB < 50 ||
        targetKB > 10000
    ) {
        showMessage(
            "uploadMessage",
            "Target must be between 50 and 10,000 KB.",
            "error"
        );

        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    const button = $("uploadButton");

    button.disabled = true;
    button.textContent = "Uploading and inspecting...";

    showMessage(
        "uploadMessage",
        "Uploading your PDF and inspecting its pages...",
        "info"
    );

    try {
        const data = await apiRequest(
            "/api/files/inspect",
            {
                method: "POST",
                body: formData
            }
        );

        currentJobId = data.job_id;

        displayInspection(data.inspection);

        $("inspectionSection").classList.remove("hidden");
        $("compressionResults").classList.add("hidden");

        $("compressionMessage").textContent = "";

        showMessage(
            "uploadMessage",
            "PDF uploaded and inspected successfully.",
            "success"
        );

        $("inspectionSection").scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        await refreshDashboard();

    } catch (error) {
        showMessage(
            "uploadMessage",
            error.message,
            "error"
        );

    } finally {
        button.disabled = false;
        button.textContent = "Upload and Inspect PDF";
    }
});


// --------------------------------------------------
// DISPLAY INSPECTION RESULTS
// --------------------------------------------------

function displayInspection(data) {
    $("inspectionFilename").textContent =
        data.filename || "-";

    $("inspectionSize").textContent =
        `${Number(data.file_size_kb).toFixed(2)} KB`;

    $("inspectionPages").textContent =
        formatNumber(data.page_count);

    $("inspectionImages").textContent =
        formatNumber(data.embedded_image_count);

    $("inspectionText").textContent =
        data.has_selectable_text ? "Yes" : "No";

    const dimensions = $("pageDimensions");

    dimensions.replaceChildren();

    for (const page of data.pages || []) {
        const row = document.createElement("div");

        row.className = "page-row";

        const left = document.createElement("span");

        left.textContent =
            `Page ${page.page} · ${page.orientation}`;

        const right = document.createElement("span");

        right.textContent =
            `${page.width} × ${page.height} pt`;

        row.append(left, right);

        dimensions.appendChild(row);
    }
}


// --------------------------------------------------
// PDF COMPRESSION
// --------------------------------------------------

$("compressButton").addEventListener("click", async function() {
    if (!currentJobId) {
        showMessage(
            "compressionMessage",
            "Upload a PDF before starting compression.",
            "error"
        );

        return;
    }

    const targetKB = Number($("targetKB").value);

    if (
        !Number.isInteger(targetKB) ||
        targetKB < 50 ||
        targetKB > 10000
    ) {
        showMessage(
            "compressionMessage",
            "Please enter a valid target size.",
            "error"
        );

        return;
    }

    const button = $("compressButton");

    button.disabled = true;
    button.textContent = "Compressing...";

    $("compressionResults").classList.add("hidden");

    showMessage(
        "compressionMessage",
        "Processing your PDF while preserving its supported content. Please wait...",
        "info"
    );

    try {
        const data = await apiRequest(
            `/api/files/${encodeURIComponent(currentJobId)}/compress`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    target_kb: targetKB
                })
            }
        );

        displayCompressionResults(data.compression);

        showMessage(
            "compressionMessage",
            data.message || "Compression completed.",
            data.compression.target_met ? "success" : "info"
        );

        await refreshDashboard();

    } catch (error) {
        showMessage(
            "compressionMessage",
            error.message,
            "error"
        );

    } finally {
        button.disabled = false;
        button.textContent = "Compress PDF";
    }
});


// --------------------------------------------------
// DISPLAY COMPRESSION RESULTS
// --------------------------------------------------

function displayCompressionResults(data) {
    $("resultOriginal").textContent =
        formatBytes(data.original_size_kb);

    $("resultCompressed").textContent =
        formatBytes(data.compressed_size_kb);

    $("resultReduction").textContent =
        `${data.reduction_percent}%`;

    $("resultPages").textContent =
        formatNumber(data.page_count);

    const status = $("compressionStatus");

    status.textContent = data.target_met
        ? "Target achieved"
        : "Target not reached";

    status.className = data.target_met
        ? "status-pill success"
        : "status-pill warning";

    $("compressionResults").classList.remove("hidden");
}


// --------------------------------------------------
// DOWNLOADS FOR CURRENT DOCUMENT
// --------------------------------------------------

$("downloadOriginal").addEventListener("click", function() {
    if (!currentJobId) return;

    window.location.href =
        `/api/files/${encodeURIComponent(currentJobId)}/download?kind=original`;
});


$("downloadCompressed").addEventListener("click", function() {
    if (!currentJobId) return;

    window.location.href =
        `/api/files/${encodeURIComponent(currentJobId)}/download?kind=compressed`;
});


// --------------------------------------------------
// PROCESSING HISTORY
// --------------------------------------------------

async function loadHistory() {
    const tableBody = $("historyTableBody");

    try {
        const data = await apiRequest("/api/history");

        tableBody.replaceChildren();

        const records = Array.isArray(data.records)
            ? data.records
            : [];

        if (!records.length) {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td colspan="7" class="empty-state">
                    No documents have been uploaded yet.
                </td>
            `;

            tableBody.appendChild(row);

            return;
        }

        for (const record of records) {
            const row = document.createElement("tr");

            const compressedSize = formatBytes(
                record.compressed_size_kb
            );

            const reduction =
                record.reduction_percent !== null &&
                record.reduction_percent !== undefined
                    ? `${record.reduction_percent}%`
                    : "-";

            const statusClass = record.target_met === true
                ? "success"
                : record.status === "completed_above_target"
                    ? "warning"
                    : "";

            row.innerHTML = `
                <td>${escapeHTML(record.filename)}</td>

                <td>${escapeHTML(formatBytes(record.original_size_kb))}</td>

                <td>${escapeHTML(formatNumber(record.page_count))}</td>

                <td>
                    <span class="status-pill ${statusClass}">
                        ${escapeHTML(formatStatus(record.status))}
                    </span>
                </td>

                <td>${escapeHTML(compressedSize)}</td>

                <td>${escapeHTML(reduction)}</td>

                <td>
                    <div class="table-actions">

                        <button
                            type="button"
                            data-action="original"
                            data-job="${escapeHTML(record.job_id)}"
                        >
                            Original
                        </button>

                        <button
                            type="button"
                            data-action="compressed"
                            data-job="${escapeHTML(record.job_id)}"
                            ${record.compressed_size_kb === null ||
                              record.compressed_size_kb === undefined
                                ? "disabled"
                                : ""}
                        >
                            Compressed
                        </button>

                    </div>
                </td>
            `;

            tableBody.appendChild(row);
        }

    } catch (error) {
        tableBody.replaceChildren();

        const row = document.createElement("tr");

        const cell = document.createElement("td");

        cell.colSpan = 7;
        cell.className = "empty-state";
        cell.textContent = error.message;

        row.appendChild(cell);
        tableBody.appendChild(row);
    }
}


// --------------------------------------------------
// HISTORY DOWNLOAD ACTIONS
// --------------------------------------------------

$("historyTableBody").addEventListener("click", function(event) {
    const button = event.target.closest("button[data-action]");

    if (!button || button.disabled) {
        return;
    }

    const jobId = button.dataset.job;
    const kind = button.dataset.action;

    if (!jobId || !["original", "compressed"].includes(kind)) {
        return;
    }

    window.location.href =
        `/api/files/${encodeURIComponent(jobId)}/download?kind=${kind}`;
});


// --------------------------------------------------
// REFRESH
// --------------------------------------------------

async function refreshDashboard() {
    await Promise.all([
        loadDashboardStats(),
        loadHistory()
    ]);
}


$("refreshButton").addEventListener("click", async function() {
    const button = $("refreshButton");

    button.disabled = true;

    try {
        await refreshDashboard();
    } finally {
        button.disabled = false;
    }
});


// --------------------------------------------------
// INITIALIZE
// --------------------------------------------------

async function initializeDashboard() {
    await loadCurrentUser();

    await refreshDashboard();
}


initializeDashboard();
