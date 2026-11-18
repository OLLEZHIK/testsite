/**
 * Pawenn outreach sender (owner, 2026-11-17).
 * Lives in the Google Sheet "Pawenn outbox" of pawenn.info@gmail.com.
 * Sends rows whose status is empty and whose send_at (UTC, ISO) has passed,
 * one row per run, through Gmail itself: links stay as written, images stay.
 *
 * Sheet columns (row 1 = header):
 *   A mail_id | B send_at | C to | D subject | E body | F html | G status | H sent_at | I message_id
 *
 * Setup (once): Extensions > Apps Script > paste this file > Save >
 * run `setup` once and allow access > done (it adds a 5-minute trigger).
 */
function setup() {
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('sendDue').timeBased().everyMinutes(5).create();
}

function sendDue() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return;
  try {
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    var rows = sh.getDataRange().getValues();
    var now = new Date();
    for (var i = 1; i < rows.length; i++) {
      var r = rows[i];
      var status = String(r[6] || '');
      if (status) continue;
      var due = new Date(r[1]);
      if (isNaN(due.getTime()) || due > now) continue;
      var to = String(r[2]).trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(to)) { sh.getRange(i + 1, 7).setValue('bad address'); continue; }
      try {
        var draft = GmailApp.createDraft(to, String(r[3]), String(r[4]), { htmlBody: String(r[5] || '') || undefined, name: 'Pawenn' });
        var msg = draft.send();
        sh.getRange(i + 1, 7, 1, 3).setValues([['sent', new Date().toISOString(), msg.getId()]]);
      } catch (e) {
        sh.getRange(i + 1, 7).setValue('error: ' + e.message);
      }
      return; // one email per run: 5+ minutes apart at least
    }
  } finally {
    lock.releaseLock();
  }
}
