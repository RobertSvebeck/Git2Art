// At most MAX_PARALLEL downloads from our own server per visitor. On the
// shared host every request holds one of the account's 30 entry processes,
// so one visitor must never fire dozens at once.

const MAX_PARALLEL = 4;
const waiting = [];
let running = 0;

function next() {
  while (running < MAX_PARALLEL && waiting.length) {
    const { task, resolve, reject } = waiting.shift();
    running += 1;
    Promise.resolve().then(task).then(resolve, reject).finally(() => {
      running -= 1;
      next();
    });
  }
}

export function throttled(task) {
  return new Promise((resolve, reject) => {
    waiting.push({ task, resolve, reject });
    next();
  });
}
