// Aschenpfad – kleiner Mehrspieler-Server (ohne Abhängigkeiten)
// Liefert das Spiel aus (http://<server>:8080) und vermittelt die Spieldaten per WebSocket (/ws).
'use strict';
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const PORT = +process.env.PORT || 8080;
const GAME = process.env.GAME_FILE || path.join(__dirname, 'index.html');
const rooms = new Map();           // Code -> { host, guest, info }
const roomList = () => [...rooms.entries()].map(([code, r]) => ({ code, full: !!r.guest, ...r.info }));
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);

const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  if (url === '/' || url === '/index.html') {
    fs.readFile(GAME, (err, data) => {
      if (err) { res.writeHead(500); res.end('index.html fehlt'); return; }
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache' }); res.end(data);
    });
  } else if (url === '/rooms') {
    res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(roomList()));
  } else if (url === '/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ ok: true, rooms: rooms.size }));
  } else { res.writeHead(404); res.end('Nicht gefunden'); }
});

// ---- minimale WebSocket-Umsetzung (RFC 6455)
function sendFrame(sock, str, opcode = 1) {
  if (sock.destroyed) return;
  const data = Buffer.from(str, 'utf8'), n = data.length;
  let head;
  if (n < 126) head = Buffer.from([0x80 | opcode, n]);
  else if (n < 65536) { head = Buffer.alloc(4); head[0] = 0x80 | opcode; head[1] = 126; head.writeUInt16BE(n, 2); }
  else { head = Buffer.alloc(10); head[0] = 0x80 | opcode; head[1] = 127; head.writeBigUInt64BE(BigInt(n), 2); }
  sock.write(Buffer.concat([head, data]));
}
const sendJSON = (c, o) => c && sendFrame(c.sock, JSON.stringify(o));

server.on('upgrade', (req, sock) => {
  if (req.url.split('?')[0] !== '/ws' || (req.headers.upgrade || '').toLowerCase() !== 'websocket') { sock.destroy(); return; }
  const key = req.headers['sec-websocket-key'];
  const accept = crypto.createHash('sha1').update(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64');
  sock.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + accept + '\r\n\r\n');
  sock.setNoDelay(true);
  const client = { sock, room: null, role: null, buf: Buffer.alloc(0), frag: [] };
  sock.on('data', chunk => {
    client.buf = Buffer.concat([client.buf, chunk]);
    for (;;) {
      const b = client.buf; if (b.length < 2) break;
      const fin = b[0] & 0x80, op = b[0] & 0x0f, masked = b[1] & 0x80; let len = b[1] & 0x7f, off = 2;
      if (len === 126) { if (b.length < 4) break; len = b.readUInt16BE(2); off = 4; }
      else if (len === 127) { if (b.length < 10) break; len = Number(b.readBigUInt64BE(2)); off = 10; }
      const mOff = off; if (masked) off += 4;
      if (b.length < off + len) break;
      let payload = b.subarray(off, off + len);
      if (masked) { const m = b.subarray(mOff, mOff + 4); payload = Buffer.from(payload); for (let i = 0; i < payload.length; i++) payload[i] ^= m[i & 3]; }
      client.buf = b.subarray(off + len);
      if (op === 8) { sock.end(); return; }
      if (op === 9) { sendFrame(sock, payload.toString(), 10); continue; }
      if (op === 10) continue;
      client.frag.push(payload);
      if (fin) { const msg = Buffer.concat(client.frag).toString('utf8'); client.frag = []; onMessage(client, msg); }
    }
  });
  const bye = () => leave(client);
  sock.on('close', bye); sock.on('error', bye);
});

function onMessage(c, msg) {
  if (msg.charCodeAt(0) === 123 && msg.startsWith('{"sys"')) {          // Steuer-Nachricht
    let m; try { m = JSON.parse(msg); } catch (e) { return; }
    const code = String(m.code || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 16);
    if (m.sys === 'host') {
      if (!code || rooms.has(code)) { sendJSON(c, { sys: 'err', why: 'taken' }); return; }
      rooms.set(code, { host: c, guest: null, info: cleanInfo(m.info) }); c.room = code; c.role = 'host'; sendJSON(c, { sys: 'hosting', code }); log('Raum', code, 'eröffnet');
    } else if (m.sys === 'info') {
      const r = c.role === 'host' && rooms.get(c.room); if (r) r.info = cleanInfo(m.info);
    } else if (m.sys === 'list') {
      sendJSON(c, { sys: 'rooms', list: roomList() });
    } else if (m.sys === 'join') {
      const r = rooms.get(code);
      if (!r) { sendJSON(c, { sys: 'err', why: 'nohost' }); return; }
      if (r.guest) { sendJSON(c, { sys: 'err', why: 'full' }); return; }
      r.guest = c; c.room = code; c.role = 'guest'; sendJSON(c, { sys: 'paired' }); sendJSON(r.host, { sys: 'paired' }); log('Raum', code, ': Mitspieler beigetreten');
    }
    return;
  }
  const r = c.room && rooms.get(c.room); if (!r) return;
  const other = c.role === 'host' ? r.guest : r.host;
  if (other) sendFrame(other.sock, msg);                                // Spieldaten 1:1 weiterreichen
}
function cleanInfo(i) {
  i = i || {}; const str = (v, n) => String(v == null ? '' : v).replace(/[<>&"]/g, '').slice(0, n);
  return { name: str(i.name, 20), lvl: Math.max(0, Math.min(999, +i.lvl || 0)), place: str(i.place, 40), act: str(i.act, 50), since: i.since || Date.now() };
}
function leave(c) {
  if (!c.room) return;
  const r = rooms.get(c.room); const code = c.room; c.room = null;
  if (!r) return;
  if (c.role === 'host') { if (r.guest) { sendJSON(r.guest, { sys: 'left' }); r.guest.room = null; } rooms.delete(code); log('Raum', code, 'geschlossen'); }
  else if (r.guest === c) { r.guest = null; sendJSON(r.host, { sys: 'left' }); log('Raum', code, ': Mitspieler gegangen'); }
}

server.listen(PORT, '0.0.0.0', () => {
  const ips = Object.values(require('os').networkInterfaces()).flat().filter(i => i && i.family === 'IPv4' && !i.internal).map(i => i.address);
  log('Aschenpfad-Server läuft auf Port ' + PORT);
  for (const ip of ips) log('  Im Browser öffnen: http://' + ip + ':' + PORT);
});
