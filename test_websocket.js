const assert = require('assert').strict;
const { spawn } = require('child_process');

const dockerjudge = require('.');

const HOST = process.env.HOST || '127.0.0.1';
const PORT = process.env.PORT || 8765;
const ADDRESS = `${HOST}:${PORT}`;

const server = spawn('coverage', ['run', '-a', '-m', 'dockerjudge', ADDRESS]);

process.on('exit', () => {
  server.kill('SIGINT');
});

const judge = () => {
  dockerjudge(`ws://${ADDRESS}/`, {
    processor: ['Python', ['3']],
    source: "print('Hello, world!')",
    tests: [['', 'Hello, world!']],
    config: {},
  }).on('error', (err) => {
    if (err.code === 'ECONNREFUSED') {
      judge();
    } else {
      throw err;
    }
  }).on('done', (args) => {
    assert.equal(args[0][0][0], 'AC');
    process.exit();
  });
};

judge();
