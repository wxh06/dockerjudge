const assert = require('assert').strict;
const { spawn } = require('child_process');

const dockerjudge = require('.');

const ADDRESS = '127.0.0.1:8765';

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
