// Offline browser QA only. npm install --prefix tools/hero-layers --no-save playwright@1.56.1
import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const shots = path.join(root, 'docs/hero-collage');
await fs.mkdir(shots, { recursive: true });
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const report = { viewports: [], scenarios: {}, consoleErrors: [] };
const url = 'http://127.0.0.1:5173/';
const pause = (page, ms) => page.waitForTimeout(ms);

async function instrument(page) {
  page.on('pageerror', (error) => report.consoleErrors.push(String(error)));
  page.on('console', (msg) => { if (msg.type() === 'error') report.consoleErrors.push(msg.text()); });
  await page.addInitScript(() => {
    window.heroQA = { frames: [], states: [], shifts: [], last: 0 };
    new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (!entry.hadRecentInput) window.heroQA.shifts.push({
          value: entry.value,
          hero: entry.sources.some(({ node }) => node?.closest?.('.hero')),
          media: entry.sources.some(({ node }) => node?.closest?.('.hero__media-wrap')),
        });
      });
    }).observe({ type: 'layout-shift', buffered: true });
    function frame(now) {
      const qa = window.heroQA;
      const state = document.querySelector('[data-collage]')?.dataset.state;
      const previous = qa.states.at(-1)?.state;
      if (state !== previous) qa.states.push({ state, at: now });
      if (state === 'entering' && previous === 'entering' && qa.last) qa.frames.push(now - qa.last);
      qa.last = now;
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  });
}

try {
  for (const width of [1280, 1024, 390]) {
    const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 }, deviceScaleFactor: 1 });
    const page = await context.newPage();
    await instrument(page);
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForFunction(() => document.querySelector('[data-collage]').dataset.state === 'settled');
    await page.evaluate(() => document.fonts.ready);
    const result = await page.evaluate(() => {
      const c = document.querySelector('[data-collage]');
      const rect = c.getBoundingClientRect();
      const qa = window.heroQA;
      const start = qa.states.find((s) => s.state === 'entering')?.at;
      const end = qa.states.find((s) => s.state === 'settled')?.at;
      return {
        width: innerWidth, mediaWidth: rect.width, mediaHeight: rect.height,
        overflow: document.documentElement.scrollWidth - innerWidth,
        entranceMs: start && end ? end - start : null,
        frameCount: qa.frames.length,
        averageFrameMs: qa.frames.reduce((a, b) => a + b, 0) / qa.frames.length,
        framesOver25ms: qa.frames.filter((v) => v > 25).length,
        maxFrameMs: Math.max(...qa.frames),
        heroCLS: qa.shifts.filter((s) => s.hero).reduce((a, s) => a + s.value, 0),
        mediaCLS: qa.shifts.filter((s) => s.media).reduce((a, s) => a + s.value, 0),
        willChange: [...c.querySelectorAll('.collage__piece')].map((el) => getComputedStyle(el).willChange),
        images: [...c.querySelectorAll('img')].map((el) => ({ url: el.currentSrc, loaded: el.complete && el.naturalWidth > 0 })),
      };
    });
    assert.equal(result.overflow, 0);
    assert(result.images.every((i) => i.loaded));
    assert(result.willChange.every((v) => v === 'auto'));
    if (width === 390) assert.equal(result.mediaWidth, 390);
    if (width !== 1024) await page.screenshot({ path: path.join(shots, `rest-${width}.png`) });
    report.viewports.push(result);

    if (width === 1280) {
      const transform = () => page.locator('[data-layer="student"]').evaluate((el) => getComputedStyle(el).transform);
      await page.mouse.move(1150, 450);
      await pause(page, 250);
      const moving = await transform();
      await page.mouse.move(100, 150);
      await pause(page, 70);
      const interrupted = await transform();
      await page.mouse.move(1279, 999);
      await pause(page, 1200);
      const returned = await transform();
      assert.notEqual(moving, 'none');
      assert.notEqual(interrupted, moving);
      assert.equal(returned, 'none');
      report.scenarios.pointer = { moving, interrupted, returned };
      await page.evaluate(() => scrollTo(0, 350));
      await pause(page, 200);
      report.scenarios.scroll = await page.locator('[data-layer="dome"]').evaluate((el) => getComputedStyle(el).transform);
      await page.evaluate(() => scrollTo(0, 1400));
      await pause(page, 200);
      assert.equal(await transform(), 'none');
      await page.evaluate(() => scrollTo(0, 0));
      await pause(page, 200);
      assert.equal(await page.locator('[data-collage]').getAttribute('data-state'), 'settled');
      report.scenarios.noReplay = true;
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await pause(page, 200);
      await page.mouse.move(1150, 450);
      await pause(page, 300);
      assert.equal(await transform(), 'none');
      report.scenarios.runtimeReducedMotion = await page.locator('.collage__piece').evaluateAll((els) => els.every((el) => getComputedStyle(el).transform === 'none' && getComputedStyle(el).opacity === '1'));
    }
    await context.close();
  }

  const reduced = await browser.newContext({ reducedMotion: 'reduce', viewport: { width: 1280, height: 1000 } });
  const reducedPage = await reduced.newPage();
  await instrument(reducedPage);
  await reducedPage.goto(url);
  await pause(reducedPage, 700);
  report.scenarios.initialReducedMotion = await reducedPage.evaluate(() => ({
    state: document.querySelector('[data-collage]').dataset.state,
    transforms: [...document.querySelectorAll('.collage__piece')].map((el) => getComputedStyle(el).transform),
    animations: document.querySelector('[data-collage]').getAnimations({ subtree: true }).length,
  }));
  assert.equal(report.scenarios.initialReducedMotion.animations, 0);
  await reduced.close();

  const noJS = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const staticPage = await noJS.newPage();
  await staticPage.goto(url);
  report.scenarios.noJS = await staticPage.locator('.collage__piece').evaluateAll((els) => els.every((el) => getComputedStyle(el).opacity === '1' && getComputedStyle(el).transform === 'none'));
  assert(report.scenarios.noJS);
  await staticPage.screenshot({ path: path.join(shots, 'no-js-390.png') });
  await noJS.close();

  const broken = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  await broken.route('**/assets/hero/student*.webp', (route) => route.abort());
  await broken.goto(url);
  await broken.waitForSelector('.collage__fallback');
  await broken.waitForFunction(() => document.querySelector('.collage__fallback').naturalWidth > 0);
  report.scenarios.brokenLayer = await broken.locator('[data-collage]').getAttribute('data-state');
  assert.equal(report.scenarios.brokenLayer, 'fallback');
  await broken.close();

  const delayed = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  await delayed.route('**/assets/hero/student*.webp', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 2400));
    await route.continue();
  });
  await instrument(delayed);
  await delayed.goto(url, { waitUntil: 'domcontentloaded' });
  await delayed.waitForFunction(() => document.querySelector('[data-collage]').dataset.state === 'settled');
  report.scenarios.timeout = await delayed.evaluate(() => window.heroQA.states);
  assert(!report.scenarios.timeout.some((state) => state.state === 'entering'));
  await pause(delayed, 2600);
  assert.equal(await delayed.locator('[data-collage]').getAttribute('data-state'), 'settled');
  await delayed.close();

  const thresholdPage = await browser.newPage({ viewport: { width: 1280, height: 150 } });
  await thresholdPage.goto(url, { waitUntil: 'domcontentloaded' });
  await pause(thresholdPage, 300);
  assert.equal(await thresholdPage.locator('[data-collage]').getAttribute('data-state'), 'waiting');
  await thresholdPage.setViewportSize({ width: 1280, height: 1000 });
  await thresholdPage.waitForFunction(() => document.querySelector('[data-collage]').dataset.state === 'entering');
  report.scenarios.visibilityThreshold = true;
  await thresholdPage.close();

  const ambientPage = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  await ambientPage.addInitScript(() => { Math.random = () => 0.1; });
  await ambientPage.goto(url);
  await ambientPage.waitForFunction(() => document.querySelector('[data-collage]').getAnimations({ subtree: true }).length > 0, null, { timeout: 12000 });
  const animated = await ambientPage.locator('[data-collage]').evaluate((el) => el.getAnimations({ subtree: true }).length);
  assert.equal(animated, 1);
  await ambientPage.evaluate(() => scrollTo(0, 1400));
  await pause(ambientPage, 100);
  assert.equal(await ambientPage.locator('[data-collage]').evaluate((el) => el.getAnimations({ subtree: true }).length), 0);
  await ambientPage.evaluate(() => scrollTo(0, 0));
  await ambientPage.waitForFunction(() => document.querySelector('[data-collage]').getAnimations({ subtree: true }).length > 0, null, { timeout: 10000 });
  // Headless Chrome does not background tabs reliably; exercise the native
  // visibility handler with a simulated hidden state and report it as such.
  await ambientPage.evaluate(() => {
    Object.defineProperty(document, 'hidden', { configurable: true, value: true });
    document.dispatchEvent(new Event('visibilitychange'));
  });
  assert.equal(await ambientPage.locator('[data-collage]').evaluate((el) => el.getAnimations({ subtree: true }).length), 0);
  report.scenarios.ambient = { simultaneousTwinkles: animated, offscreenCancellation: true, simulatedHiddenCancellation: true };
  await ambientPage.close();

  const slowPage = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  await slowPage.goto(url + '?slow=10', { waitUntil: 'domcontentloaded' });
  await slowPage.waitForFunction(() => document.querySelector('[data-collage]').dataset.state === 'entering');
  let elapsed = 0;
  for (const at of [2500, 5000, 8000, 11000]) {
    await pause(slowPage, at - elapsed);
    await slowPage.screenshot({ path: path.join(shots, `entrance-${at}.png`) });
    elapsed = at;
  }
  report.scenarios.slowFrames = 4;
  await slowPage.emulateMedia({ reducedMotion: 'reduce' });
  await slowPage.waitForFunction(() => document.querySelector('[data-collage]').dataset.state === 'settled');
  report.scenarios.reduceDuringEntrance = await slowPage.locator('.collage__piece').evaluateAll((els) => els.every((el) => getComputedStyle(el).transform === 'none' && getComputedStyle(el).opacity === '1' && getComputedStyle(el).willChange === 'auto'));
  assert(report.scenarios.reduceDuringEntrance);
  await slowPage.close();
} finally {
  await fs.writeFile(path.join(root, 'tools/hero-layers/out/browser-report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  await browser.close();
}
