
import * as vscode from 'vscode';
import axios from 'axios';
import * as path from 'path';

// Constants
const API_URL = 'http://localhost:8000';
const DIAGNOSTIC_COLLECTION = vscode.languages.createDiagnosticCollection('ibd');

export function activate(context: vscode.ExtensionContext) {
    console.log('IBD Extension is active!');

    // Command: Analyze File
    let disposableAnalyze = vscode.commands.registerCommand('ibd.analyzeFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No file is open to analyze.');
            return;
        }

        const document = editor.document;
        const filePath = document.fileName;
        const fileContent = document.getText();

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing File...",
            cancellable: false
        }, async (progress) => {
            try {
                // Call Backend
                const response = await axios.post(`${API_URL}/analyze_file`, {
                    path: filePath,
                    content: fileContent
                });

                const issues = response.data.issues;
                updateDiagnostics(document, issues);

                vscode.window.showInformationMessage(`Analysis complete. Found ${issues.length} issues.`);
            } catch (error: any) {
                console.error(error);
                vscode.window.showErrorMessage(`Analysis failed: ${error.message || error}`);
            }
        });
    });

    // Command: Repair File (Safe Copy)
    let disposableRepair = vscode.commands.registerCommand('ibd.repairFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No file is open to repair.');
            return;
        }

        const document = editor.document;
        const filePath = document.fileName;
        const fileContent = document.getText();

        // Ask for bug description if manual, or use auto-detection
        // For prototype, we'll try to auto-fix everything found

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Generating Fix (Safe Copy)...",
            cancellable: false
        }, async (progress) => {
            try {
                // Call Backend
                const response = await axios.post(`${API_URL}/repair_file_safe`, {
                    path: filePath,
                    content: fileContent
                });

                const fixedPath = response.data.fixed_path;

                // Open side-by-side diff
                const fixedUri = vscode.Uri.file(fixedPath);
                await vscode.commands.executeCommand('vscode.diff', document.uri, fixedUri, 'Original vs Fixed');

                vscode.window.showInformationMessage(`Fix generated at: ${fixedPath}`);
            } catch (error: any) {
                console.error(error);
                vscode.window.showErrorMessage(`Repair failed: ${error.message || error}`);
            }
        });
    });

    context.subscriptions.push(disposableAnalyze);
    context.subscriptions.push(disposableRepair);
    context.subscriptions.push(DIAGNOSTIC_COLLECTION);
}

function updateDiagnostics(document: vscode.TextDocument, issues: any[]) {
    const diagnostics: vscode.Diagnostic[] = [];

    for (const issue of issues) {
        // Convert 1-based line to 0-based
        const line = Math.max(0, (issue.line || 1) - 1);
        const range = new vscode.Range(line, 0, line, Number.MAX_VALUE);

        const severity = issue.severity === 'critical' ? vscode.DiagnosticSeverity.Error :
            issue.severity === 'high' ? vscode.DiagnosticSeverity.Warning :
                vscode.DiagnosticSeverity.Information;

        const diagnostic = new vscode.Diagnostic(range, `${issue.message} [${issue.type}]`, severity);
        diagnostic.source = 'IBD AI';
        diagnostics.push(diagnostic);
    }

    DIAGNOSTIC_COLLECTION.set(document.uri, diagnostics);
}

export function deactivate() { }
