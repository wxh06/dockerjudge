const EventEmitter = require('events');

const WebSocket = require('ws');

module.exports = (url, args) => {
  const emitter = new EventEmitter();
  const ws = new WebSocket(url);
  emitter.ws = ws;
  ws.on('error', (err) => {
    emitter.emit('error', err);
  });
  ws.on('open', () => {
    ws.send(JSON.stringify(args));
    ws.on('message', (json) => {
      const data = JSON.parse(json);
      emitter.emit(...data);
    });
  });
  return emitter;
};
