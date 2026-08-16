'use strict';

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = (function() { let dir = process.env.PROJECT_ROOT || process.cwd(); while (dir !== path.dirname(dir)) { if (fs.existsSync(path.join(dir, '.git')) || fs.existsSync(path.join(dir, 'notes'))) return dir; dir = path.dirname(dir); } return process.env.PROJECT_ROOT || process.cwd(); })();
const NOTES_DIR = path.join(PROJECT_ROOT, 'notes');
const TEMP_DIR = path.join(NOTES_DIR, 'temp');

function readTextFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch (e) {
    return null;
  }
}

function extractReferences(content) {
  var refs = [];
  var negCC = "[^\\s`<>)}\\]:" + String.fromCharCode(39) + ",\x22]";
  // Pattern 1: src/ paths (JS/TS projects)
  var srcPattern = new RegExp("`?(([\\w.-]+/)*src/" + negCC + "+)(?::(\\d+))?`?", "g");
  // Pattern 2: common non-src paths (Python/Django, Java, Go, etc.)
  // Matches: application/xxx.py, app/xxx.py, lib/xxx.py, pkg/xxx.go, com/xxx.java, etc.
  var generalPattern = new RegExp("`?(([\\w.-]+/){1,4}[\\w.-]+\\.(py|java|go|rb|rs|ts|js|tsx|jsx|vue|yaml|yml|json|toml))(?::(\\d+))?`?", "g");
  var seen = new Set();
  var match;

  while ((match = srcPattern.exec(content)) !== null) {
    var refPath = match[1];
    var line = match[3] ? parseInt(match[3], 10) : null;
    var key = line != null ? refPath + ':' + line : refPath;
    if (!seen.has(key)) {
      seen.add(key);
      refs.push({ path: refPath, line: line });
    }
  }

  while ((match = generalPattern.exec(content)) !== null) {
    var refPath = match[1];
    var line = match[5] ? parseInt(match[5], 10) : null;
    var key = line != null ? refPath + ':' + line : refPath;
    if (!seen.has(key)) {
      seen.add(key);
      refs.push({ path: refPath, line: line });
    }
  }

  return refs;
}

function checkLineReference(filePath, line, content) {
  const lines = content.split('\n');
  if (line < 1 || line > lines.length) {
    return { match: false, reason: 'line-out-of-range' };
  }
  return { match: true, lineContent: lines[line - 1].trim() };
}

function extractMetadata(content) {
  const metaMatch = content.match(/<!--\s*\n\s*last-checked:\s*(\S+)\s*\n\s*last-updated:\s*(\S+)\s*\n\s*-->/);
  if (metaMatch) {
    return { lastChecked: metaMatch[1], lastUpdated: metaMatch[2] };
  }
  const checkedMatch = content.match(/last-checked:\s*(\S+)/);
  const updatedMatch = content.match(/last-updated:\s*(\S+)/);
  return {
    lastChecked: checkedMatch ? checkedMatch[1] : null,
    lastUpdated: updatedMatch ? updatedMatch[1] : null,
  };
}

function countChangeHistoryEntries(content) {
  const sectionMatch = content.match(/## 变更历史\s*\n([\s\S]*?)(?=\n## |<!--|$)/);
  if (!sectionMatch) return { count: 0, hasSection: false };
  const tableRows = sectionMatch[1].match(/^\|.*\|.*\|$/gm);
  if (!tableRows) return { count: 0, hasSection: true };
  const dataRows = tableRows.filter(function (row) {
    return !row.match(/^\|\s*[-:|]+\s*\|/);
  });
  return { count: dataRows.length, hasSection: true };
}

function processDocument(filePath) {
  const content = readTextFile(filePath);
  if (!content) return null;

  const fileName = path.relative(PROJECT_ROOT, filePath).replace(/\\/g, '/');
  const metadata = extractMetadata(content);
  const rawRefs = extractReferences(content);

  const uniqueRefs = [];
  const seen = new Set();
  for (const ref of rawRefs) {
    const key = ref.line != null ? `${ref.path}:${ref.line}` : ref.path;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueRefs.push(ref);
    }
  }

  const references = [];
  const missingReferences = [];
  const shiftedReferences = [];

  for (const ref of uniqueRefs) {
    const absPath = path.join(PROJECT_ROOT, ref.path);
    const fileContent = readTextFile(absPath);
    let exists = fileContent !== null;
    // 引用一个真实存在的目录是合法的（如 "src/panel/skin/"），不计为缺失
    if (!exists) {
      try { exists = fs.statSync(absPath).isDirectory(); } catch (e) {}
    }

    const refEntry = { path: ref.path, exists: exists };
    if (ref.line != null) {
      refEntry.line = ref.line;
      if (exists) {
        const lineCheck = checkLineReference(absPath, ref.line, fileContent);
        if (lineCheck.match) {
          refEntry.lineMatch = 'shift';
        } else {
          shiftedReferences.push({ path: ref.path, line: ref.line, reason: lineCheck.reason });
        }
      }
    }

    references.push(refEntry);
    if (!exists) {
      missingReferences.push(ref.path);
    }
  }

  return {
    file: fileName,
    lastChecked: metadata.lastChecked,
    lastUpdated: metadata.lastUpdated,
    references: references,
    missingReferences: missingReferences,
    shiftedReferences: shiftedReferences,
    changeHistory: countChangeHistoryEntries(content),
  };
}

function processTempDir() {
  let tempFiles = [];
  try {
    tempFiles = fs.readdirSync(TEMP_DIR).filter(function (f) { return f.endsWith('.md'); });
  } catch (e) {
    return { count: 0, oldestFile: null, oldestDate: null };
  }

  if (tempFiles.length === 0) {
    return { count: 0, oldestFile: null, oldestDate: null };
  }

  let oldestTime = Infinity;
  let oldestFile = null;

  for (const f of tempFiles) {
    const stat = fs.statSync(path.join(TEMP_DIR, f));
    if (stat.mtimeMs < oldestTime) {
      oldestTime = stat.mtimeMs;
      oldestFile = f;
    }
  }

  const oldestDate = oldestTime < Infinity
    ? new Date(oldestTime).toISOString().split('T')[0]
    : null;

  return {
    count: tempFiles.length,
    oldestFile: oldestFile,
    oldestDate: oldestDate,
  };
}

function main() {
  let docFiles = [];
  try {
    docFiles = fs.readdirSync(NOTES_DIR)
      .filter(function (f) { return f.endsWith('.md'); })
      .sort();
  } catch (e) {
    console.error('notes/ directory not found');
    process.exit(1);
  }

  const documents = [];
  let totalMissing = 0;
  let totalShifted = 0;
  let changeHistoryOverflow = 0;

  for (const doc of docFiles) {
    const result = processDocument(path.join(NOTES_DIR, doc));
    if (result) {
      documents.push(result);
      totalMissing += result.missingReferences.length;
      totalShifted += result.shiftedReferences.length;
      if (result.changeHistory.count > 5) {
        changeHistoryOverflow++;
      }
    }
  }

  const temp = processTempDir();

  var contentDuplication = detectContentDuplication(docFiles);

  const output = {
    documents: documents,
    temp: temp,
    contentDuplication: contentDuplication,
    summary: {
      totalDocuments: documents.length,
      missingFiles: totalMissing,
      shiftedLines: totalShifted,
      tempBacklog: temp.count >= 5,
      changeHistoryOverflow: changeHistoryOverflow,
      duplicatedTopics: contentDuplication.length,
    },
  };

  console.log(JSON.stringify(output, null, 2));
}

function detectContentDuplication(docFiles) {
  var HEADING_PATTERN = /^#{1,3}\s+(.+)$/gm;
  var docHeadings = {};
  var duplicates = [];

  for (var i = 0; i < docFiles.length; i++) {
    var filePath = path.join(NOTES_DIR, docFiles[i]);
    var content = readTextFile(filePath);
    if (!content) continue;

    var headings = [];
    var m;
    var pattern = new RegExp(HEADING_PATTERN.source, 'gm');
    while ((m = pattern.exec(content)) !== null) {
      headings.push(m[1].replace(/`[^`]+`/g, '').trim());
    }
    docHeadings[docFiles[i]] = headings;
  }

  var files = Object.keys(docHeadings);
  for (var a = 0; a < files.length; a++) {
    for (var b = a + 1; b < files.length; b++) {
      var common = [];
      var ha = docHeadings[files[a]];
      var hb = docHeadings[files[b]];
      for (var x = 0; x < ha.length; x++) {
        for (var y = 0; y < hb.length; y++) {
          if (ha[x].length > 6 && ha[x] === hb[y]) {
            common.push(ha[x]);
          }
        }
      }
      if (common.length > 0) {
        duplicates.push({
          docA: files[a],
          docB: files[b],
          commonHeadings: common,
        });
      }
    }
  }

  return duplicates;
}

main();
