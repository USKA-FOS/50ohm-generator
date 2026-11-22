/*
 * Morse sounder: plays [morse:...] elements as audio (see 50ohm-contents-ch#10).
 *
 * The HTML renderer emits
 *   <span class="morse morse-playable" data-morse="12 3 2111" ...>
 * where characters are separated by spaces and each character is a string of
 * symbols: 1 = dit, 2 = dah, 3 = word gap. Each child span.morse_char matches
 * one character, so the character currently sounding can be highlighted.
 *
 * Timing (PARIS standard): dit = 1 unit, dah = 3 units, gap inside a
 * character = 1 unit, between characters = 3 units, between words = 7 units,
 * unit = 1200 / WPM milliseconds.
 *
 * Optional overrides: data-wpm / data-tone on the element, or the globals
 * window.MORSE_SOUNDER_WPM / window.MORSE_SOUNDER_TONE.
 */
(function () {
  "use strict";

  var DEFAULT_WPM = 18;
  var DEFAULT_TONE_HZ = 600;
  var RAMP_S = 0.005; // short attack/release to avoid clicks
  var VOLUME = 0.3;

  var audioCtx = null;
  var current = null; // { el, osc, gain, timers }

  function getAudioContext() {
    if (!audioCtx) {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return null;
      audioCtx = new Ctx();
    }
    if (audioCtx.state === "suspended") audioCtx.resume();
    return audioCtx;
  }

  function numberSetting(el, attr, globalName, fallback) {
    var v = parseFloat(el.getAttribute(attr));
    if (!(v > 0)) v = parseFloat(window[globalName]);
    return v > 0 ? v : fallback;
  }

  function parse(el) {
    var data = (el.getAttribute("data-morse") || "").trim();
    return data ? data.split(/\s+/) : [];
  }

  function stop() {
    if (!current) return;
    var c = current;
    current = null;
    c.timers.forEach(clearTimeout);
    try {
      var now = c.osc.context.currentTime;
      c.gain.gain.cancelScheduledValues(now);
      c.gain.gain.setValueAtTime(c.gain.gain.value, now);
      c.gain.gain.linearRampToValueAtTime(0, now + RAMP_S);
      c.osc.stop(now + RAMP_S * 2);
    } catch (e) {
      /* oscillator already stopped */
    }
    c.el.classList.remove("morse-playing");
    c.el.querySelectorAll(".morse_char.morse-active").forEach(function (ch) {
      ch.classList.remove("morse-active");
    });
  }

  function play(el) {
    var ctx = getAudioContext();
    if (!ctx) return;

    var chars = parse(el);
    if (!chars.length) return;

    var unit = 1.2 / numberSetting(el, "data-wpm", "MORSE_SOUNDER_WPM", DEFAULT_WPM);
    var tone = numberSetting(el, "data-tone", "MORSE_SOUNDER_TONE", DEFAULT_TONE_HZ);

    var osc = ctx.createOscillator();
    var gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = tone;
    gain.gain.value = 0;
    osc.connect(gain).connect(ctx.destination);

    var start = ctx.currentTime + 0.05;
    var t = start;
    var timers = [];
    var charEls = el.querySelectorAll(".morse_char");

    function at(time, fn) {
      timers.push(setTimeout(fn, Math.max(0, time - ctx.currentTime) * 1000));
    }

    function highlight(index, from, to) {
      var ch = charEls[index];
      if (!ch) return;
      at(from, function () { ch.classList.add("morse-active"); });
      at(to, function () { ch.classList.remove("morse-active"); });
    }

    chars.forEach(function (ch, index) {
      if (ch === "3") {
        // Word gap: 3 units already follow the previous character, add 4 more.
        t += 4 * unit;
        return;
      }
      var tStart = t;
      for (var i = 0; i < ch.length; i++) {
        var len = ch[i] === "2" ? 3 * unit : unit;
        gain.gain.setValueAtTime(0, t);
        gain.gain.linearRampToValueAtTime(VOLUME, t + RAMP_S);
        gain.gain.setValueAtTime(VOLUME, t + len - RAMP_S);
        gain.gain.linearRampToValueAtTime(0, t + len);
        t += len + unit; // symbol + intra-character gap
      }
      highlight(index, tStart, t - unit);
      t += 2 * unit; // complete the 3-unit inter-character gap
    });

    osc.start(start);
    osc.stop(t);

    current = { el: el, osc: osc, gain: gain, timers: timers };
    el.classList.add("morse-playing");

    var mine = current;
    osc.onended = function () {
      if (current === mine) stop();
    };
  }

  function toggle(el) {
    var wasPlaying = current && current.el === el;
    stop();
    if (!wasPlaying) play(el);
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest(".morse-playable");
    if (el) toggle(el);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var el = e.target.closest && e.target.closest(".morse-playable");
    if (!el) return;
    e.preventDefault();
    toggle(el);
  });

  window.MorseSounder = { play: play, stop: stop };
})();
