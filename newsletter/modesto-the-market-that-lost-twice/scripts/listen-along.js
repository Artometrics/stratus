(function () {
  "use strict";

  var audio = document.getElementById("wp-audio");
  if (!audio) return;

  var SKIP = 15;
  var SPEEDS = [0.75, 1, 1.25, 1.5, 1.75, 2];
  var STORAGE_KEY = "wp-audio-rate";

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function formatTime(sec) {
    if (!isFinite(sec) || sec < 0) return "00:00";
    var m = Math.floor(sec / 60);
    var s = Math.floor(sec % 60);
    return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
  }

  function formatSpeed(rate) {
    if (rate === 1) return "1×";
    var s = String(rate);
    return s.replace(/\.0$/, "") + "×";
  }

  function clamp(t, max) {
    return Math.max(0, Math.min(t, max || 0));
  }

  function speedIndex(rate) {
    var i = SPEEDS.indexOf(rate);
    return i >= 0 ? i : SPEEDS.indexOf(1);
  }

  function setSpeed(rate) {
    if (SPEEDS.indexOf(rate) < 0) rate = 1;
    audio.playbackRate = rate;
    $$('[data-role="speed-label"]').forEach(function (el) {
      el.textContent = formatSpeed(rate);
    });
    $$('[data-action="speed-dial"]').forEach(function (btn) {
      btn.setAttribute("aria-label", "Playback speed " + formatSpeed(rate));
    });
    try {
      sessionStorage.setItem(STORAGE_KEY, String(rate));
    } catch (e) {}
  }

  function cycleSpeed() {
    var i = speedIndex(audio.playbackRate);
    setSpeed(SPEEDS[(i + 1) % SPEEDS.length]);
  }

  function bindPanel(root) {
    if (!root || root.dataset.wpBound) return;
    root.dataset.wpBound = "1";

    var playBtn = $('[data-action="play-pause"]', root);
    var backBtn = $('[data-action="back-15"]', root);
    var fwdBtn = $('[data-action="forward-15"]', root);
    var seek = $('[data-action="seek"]', root);
    var speedDial = $('[data-action="speed-dial"]', root);
    var curEl = $('[data-role="time-current"]', root);
    var durEl = $('[data-role="time-duration"]', root);

    function syncPlayState() {
      var playing = !audio.paused;
      if (playBtn) {
        playBtn.setAttribute("aria-pressed", playing ? "true" : "false");
        playBtn.setAttribute("aria-label", playing ? "Pause" : "Play");
      }
    }

    function syncProgress() {
      var d = audio.duration;
      var c = audio.currentTime;
      if (seek && isFinite(d) && d > 0) {
        seek.value = String((c / d) * 100);
        seek.max = "100";
      }
      if (curEl) curEl.textContent = formatTime(c);
      if (durEl) durEl.textContent = formatTime(d);
    }

    if (playBtn) {
      playBtn.addEventListener("click", function () {
        if (audio.paused) audio.play();
        else audio.pause();
      });
    }
    if (backBtn) {
      backBtn.addEventListener("click", function () {
        audio.currentTime = clamp(audio.currentTime - SKIP, audio.duration || 0);
      });
    }
    if (fwdBtn) {
      fwdBtn.addEventListener("click", function () {
        audio.currentTime = clamp(audio.currentTime + SKIP, audio.duration || 0);
      });
    }
    if (seek) {
      seek.addEventListener("input", function () {
        var d = audio.duration;
        if (!isFinite(d)) return;
        audio.currentTime = (parseFloat(seek.value, 10) / 100) * d;
      });
    }
    if (speedDial) {
      speedDial.addEventListener("click", cycleSpeed);
    }

    audio.addEventListener("play", syncPlayState);
    audio.addEventListener("pause", syncPlayState);
    audio.addEventListener("timeupdate", syncProgress);
    audio.addEventListener("loadedmetadata", syncProgress);
    audio.addEventListener("durationchange", syncProgress);

    syncPlayState();
    syncProgress();
  }

  $$(".wp-listen-panel").forEach(bindPanel);

  var saved = parseFloat(sessionStorage.getItem(STORAGE_KEY), 10);
  setSpeed(SPEEDS.indexOf(saved) >= 0 ? saved : 1);

  document.addEventListener("keydown", function (e) {
    var tag = (e.target && e.target.tagName) || "";
    if (/^(INPUT|TEXTAREA|SELECT|BUTTON)$/.test(tag)) return;
    if (e.target && e.target.isContentEditable) return;
    if (e.code === "Space") {
      e.preventDefault();
      if (audio.paused) audio.play();
      else audio.pause();
    } else if (e.code === "ArrowLeft") {
      audio.currentTime = clamp(audio.currentTime - SKIP, audio.duration || 0);
    } else if (e.code === "ArrowRight") {
      audio.currentTime = clamp(audio.currentTime + SKIP, audio.duration || 0);
    }
  });
})();
