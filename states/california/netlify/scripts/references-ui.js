(function () {
  "use strict";

  var mount = document.getElementById("ref-hub");
  if (!mount) return;

  var rosterEl = document.getElementById("ref-roster-label");
  var rosterLabel = rosterEl ? rosterEl.textContent.trim() : "";

  var STYLES = [
    { id: "apa", label: "APA 7" },
    { id: "chicago", label: "Chicago" },
    { id: "mla", label: "MLA 9" },
  ];

  var REFS = [
    {
      apa: 'Centers for Medicare &amp; Medicaid Services. (2024). <em>Medicare and Medicaid programs and the Children’s Health Insurance Program; hospital inpatient prospective payment systems for acute care hospitals and the long-term care hospital prospective payment system and policy changes and fiscal year 2025 rates</em> (Final rule). 89 Fed. Reg. 68986. https://www.federalregister.gov/d/2024-17021',
      chicago:
        'Centers for Medicare &amp; Medicaid Services. 2024. “Medicare and Medicaid Programs and the Children’s Health Insurance Program; Hospital Inpatient Prospective Payment Systems for Acute Care Hospitals and the Long-Term Care Hospital Prospective Payment System and Policy Changes and Fiscal Year 2025 Rates.” <em>Federal Register</em> 89:68986. https://www.federalregister.gov/d/2024-17021',
      mla: 'Centers for Medicare &amp; Medicaid Services. “Medicare and Medicaid Programs and the Children’s Health Insurance Program; Hospital Inpatient Prospective Payment Systems for Acute Care Hospitals and the Long-Term Care Hospital Prospective Payment System and Policy Changes and Fiscal Year 2025 Rates.” <em>Federal Register</em>, 2024, https://www.federalregister.gov/d/2024-17021.',
    },
    {
      apa: 'Centers for Medicare &amp; Medicaid Services. (2025). <em>Medicare program; hospital inpatient prospective payment systems for acute care hospitals and the long-term care hospital prospective payment system and policy changes and fiscal year 2026 rates</em> (Final rule, CMS-1833-F). 90 Fed. Reg. 36536. https://www.federalregister.gov/d/2025-14681',
      chicago:
        'Centers for Medicare &amp; Medicaid Services. 2025. “Medicare Program; Hospital Inpatient Prospective Payment Systems for Acute Care Hospitals and the Long-Term Care Hospital Prospective Payment System and Policy Changes and Fiscal Year 2026 Rates.” <em>Federal Register</em> 90:36536. https://www.federalregister.gov/d/2025-14681',
      mla: 'Centers for Medicare &amp; Medicaid Services. “Medicare Program; Hospital Inpatient Prospective Payment Systems for Acute Care Hospitals and the Long-Term Care Hospital Prospective Payment System and Policy Changes and Fiscal Year 2026 Rates.” <em>Federal Register</em>, 2025, https://www.federalregister.gov/d/2025-14681.',
    },
    {
      apa: 'Centers for Medicare &amp; Medicaid Services. (2026a). <em>Medicare program; hospital inpatient prospective payment systems for acute care hospitals and the long-term care hospital prospective payment system and policy changes and fiscal year 2027 rates</em> (Final rule, CMS-1849-F). 91 Fed. Reg. 49570. https://www.federalregister.gov/d/2026-15833',
      chicago:
        'Centers for Medicare &amp; Medicaid Services. 2026. “Medicare Program; Hospital Inpatient Prospective Payment Systems for Acute Care Hospitals and the Long-Term Care Hospital Prospective Payment System and Policy Changes and Fiscal Year 2027 Rates.” <em>Federal Register</em> 91:49570. https://www.federalregister.gov/d/2026-15833',
      mla: 'Centers for Medicare &amp; Medicaid Services. “Medicare Program; Hospital Inpatient Prospective Payment Systems for Acute Care Hospitals and the Long-Term Care Hospital Prospective Payment System and Policy Changes and Fiscal Year 2027 Rates.” <em>Federal Register</em>, 2026, https://www.federalregister.gov/d/2026-15833.',
    },
    {
      apa: 'Centers for Medicare &amp; Medicaid Services. (2026b). <em>Transforming Episode Accountability Model participant list</em> (__ROSTER__). https://www.cms.gov/team-model-participant-list',
      chicago:
        'Centers for Medicare &amp; Medicaid Services. 2026. “Transforming Episode Accountability Model Participant List.” __ROSTER__. https://www.cms.gov/team-model-participant-list',
      mla: 'Centers for Medicare &amp; Medicaid Services. “Transforming Episode Accountability Model Participant List.” __ROSTER__, https://www.cms.gov/team-model-participant-list.',
    },
    {
      apa: 'Centers for Medicare &amp; Medicaid Services. (2026c). <em>Hospital Readmissions Reduction Program</em> [Data set, 9n3s-kdb3]. CMS Provider Data Catalog. https://data.cms.gov/provider-data/dataset/9n3s-kdb3',
      chicago:
        'Centers for Medicare &amp; Medicaid Services. 2026. “Hospital Readmissions Reduction Program.” CMS Provider Data Catalog, dataset 9n3s-kdb3. https://data.cms.gov/provider-data/dataset/9n3s-kdb3',
      mla: 'Centers for Medicare &amp; Medicaid Services. “Hospital Readmissions Reduction Program.” <em>CMS Provider Data Catalog</em>, dataset 9n3s-kdb3, 2026, https://data.cms.gov/provider-data/dataset/9n3s-kdb3.',
    },
    {
      apa: 'Dummit, L. A., Kahvecioglu, D., Marrufo, G., Rajkumar, R., Marshall, J., Tan, E., Press, M. J., Flood, S., Muldoon, L. D., Gu, Q., Hassol, A., Bott, D. M., Bassano, A., &amp; Conway, P. H. (2016). Association between hospital participation in a Medicare bundled payment initiative and payments and quality outcomes for lower extremity joint replacement episodes. <em>JAMA, 316</em>(12), 1267–1278. https://doi.org/10.1001/jama.2016.12717',
      chicago:
        'Dummit, Laura A., Deniz Kahvecioglu, Grecia Marrufo, Rahul Rajkumar, Julia Marshall, Eric Tan, Matthew J. Press, Steven Flood, Laura D. Muldoon, Qian Gu, Adam Hassol, Daniel M. Bott, Anthony Bassano, and Patrick H. Conway. 2016. “Association between Hospital Participation in a Medicare Bundled Payment Initiative and Payments and Quality Outcomes for Lower Extremity Joint Replacement Episodes.” <em>JAMA</em> 316, no. 12: 1267–78. https://doi.org/10.1001/jama.2016.12717',
      mla: 'Dummit, Laura A., et al. “Association between Hospital Participation in a Medicare Bundled Payment Initiative and Payments and Quality Outcomes for Lower Extremity Joint Replacement Episodes.” <em>JAMA</em>, vol. 316, no. 12, 2016, pp. 1267–78, https://doi.org/10.1001/jama.2016.12717.',
    },
    {
      apa: 'Finkelstein, A., Ji, Y., Mahoney, N., &amp; Skinner, J. (2018). Mandatory Medicare bundled payment program for lower extremity joint replacement and discharge to institutional postacute care: Interim analysis of the first year of a 5-year randomized trial. <em>JAMA, 320</em>(9), 892–900. https://doi.org/10.1001/jama.2018.12346',
      chicago:
        'Finkelstein, Amy, Yunan Ji, Neale Mahoney, and Jonathan Skinner. 2018. “Mandatory Medicare Bundled Payment Program for Lower Extremity Joint Replacement and Discharge to Institutional Postacute Care.” <em>JAMA</em> 320, no. 9: 892–900. https://doi.org/10.1001/jama.2018.12346',
      mla: 'Finkelstein, Amy, et al. “Mandatory Medicare Bundled Payment Program for Lower Extremity Joint Replacement and Discharge to Institutional Postacute Care.” <em>JAMA</em>, vol. 320, no. 9, 2018, pp. 892–900, https://doi.org/10.1001/jama.2018.12346.',
    },
    {
      apa: '<em>Quality measures, composite quality score, and display of quality measures</em>, 42 C.F.R. § 512.547 (2026). https://www.ecfr.gov/current/title-42/section-512.547',
      chicago:
        'Quality Measures, Composite Quality Score, and Display of Quality Measures. 42 C.F.R. § 512.547 (2026). https://www.ecfr.gov/current/title-42/section-512.547',
      mla: '<em>Quality Measures, Composite Quality Score, and Display of Quality Measures</em>. 42 C.F.R. § 512.547, 2026, https://www.ecfr.gov/current/title-42/section-512.547.',
    },
    {
      apa: 'Rainfall Health. (2026a). <em>Comments on the proposed Comprehensive Care for Joint Replacement Expanded (CJR-X) Model</em>. https://www.rainfallhealth.com/documents/cms-comments/rainfall-health-cjr-x-comment-letter-2026-06-08.pdf',
      chicago:
        'Rainfall Health. 2026. “Comments on the Proposed Comprehensive Care for Joint Replacement Expanded (CJR-X) Model.” https://www.rainfallhealth.com/documents/cms-comments/rainfall-health-cjr-x-comment-letter-2026-06-08.pdf',
      mla: 'Rainfall Health. “Comments on the Proposed Comprehensive Care for Joint Replacement Expanded (CJR-X) Model.” 2026, https://www.rainfallhealth.com/documents/cms-comments/rainfall-health-cjr-x-comment-letter-2026-06-08.pdf.',
    },
    {
      apa: 'Rainfall Health. (2026b). <em>CMS TEAM participating hospitals: California</em>. https://www.rainfallhealth.com/cms-team/participating-hospitals/california/',
      chicago:
        'Rainfall Health. 2026. “CMS TEAM Participating Hospitals: California.” https://www.rainfallhealth.com/cms-team/participating-hospitals/california/',
      mla: 'Rainfall Health. “CMS TEAM Participating Hospitals: California.” 2026, https://www.rainfallhealth.com/cms-team/participating-hospitals/california/.',
    },
    {
      apa: 'Zuckerman, R. B., Sheingold, S. H., Orav, E. J., Ruhter, J., &amp; Epstein, A. M. (2016). Readmissions, observation, and the Hospital Readmissions Reduction Program. <em>New England Journal of Medicine, 374</em>(16), 1543–1551. https://doi.org/10.1056/NEJMsa1513024',
      chicago:
        'Zuckerman, Rachael B., Steven H. Sheingold, E. John Orav, Julie Ruhter, and Arnold M. Epstein. 2016. “Readmissions, Observation, and the Hospital Readmissions Reduction Program.” <em>New England Journal of Medicine</em> 374, no. 16: 1543–51. https://doi.org/10.1056/NEJMsa1513024',
      mla: 'Zuckerman, Rachael B., et al. “Readmissions, Observation, and the Hospital Readmissions Reduction Program.” <em>New England Journal of Medicine</em>, vol. 374, no. 16, 2016, pp. 1543–51, https://doi.org/10.1056/NEJMsa1513024.',
    },
  ];

  var activeStyle = "apa";
  var toastTimer;

  function applyRoster(html) {
    if (!rosterLabel) return html;
    return html.split("__ROSTER__").join("(" + rosterLabel + ")");
  }

  function linkifyHtml(html) {
    return html.replace(
      /(https?:\/\/[^\s<]+)/g,
      '<a class="ref-link" href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
  }

  function plainText(html) {
    var el = document.createElement("div");
    el.innerHTML = html;
    return (el.textContent || el.innerText || "").replace(/\s+/g, " ").trim();
  }

  function render(style) {
    activeStyle = style;
    var list = mount.querySelector(".ref-list");
    if (!list) return;
    list.innerHTML = REFS.map(function (ref, i) {
      var body = applyRoster(ref[style] || ref.apa);
      var copy = plainText(body);
      return (
        '<article class="ref-card" tabindex="0" role="button" data-ref-index="' +
        i +
        '" aria-label="Copy reference ' +
        (i + 1) +
        '">' +
        '<p class="ref-card-text">' +
        linkifyHtml(body) +
        "</p>" +
        '<span class="ref-card-meta">Copy</span>' +
        '<textarea class="ref-card-copy" aria-hidden="true" tabindex="-1">' +
        copy +
        "</textarea></article>"
      );
    }).join("");
  }

  function setTab(style) {
    mount.querySelectorAll(".ref-tab").forEach(function (btn) {
      var on = btn.getAttribute("data-ref-style") === style;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    render(style);
  }

  function showToast(msg) {
    var toast = mount.querySelector(".ref-toast");
    if (!toast) return;
    toast.textContent = msg;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.hidden = true;
    }, 2000);
  }

  function copyCard(card) {
    var ta = card.querySelector(".ref-card-copy");
    var text = ta ? ta.value : "";
    if (!text) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () {
          showToast("Copied to clipboard");
        },
        function () {
          fallbackCopy(ta);
        }
      );
    } else {
      fallbackCopy(ta);
    }
    card.classList.add("is-copied");
    setTimeout(function () {
      card.classList.remove("is-copied");
    }, 1200);
  }

  function fallbackCopy(ta) {
    ta.removeAttribute("aria-hidden");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    ta.select();
    try {
      document.execCommand("copy");
      showToast("Copied to clipboard");
    } catch (e) {
      showToast("Could not copy");
    }
    ta.setAttribute("aria-hidden", "true");
  }

  mount.innerHTML =
    '<div class="ref-toolbar">' +
    '<div class="ref-tabs" role="tablist" aria-label="Citation style">' +
    STYLES.map(function (s, i) {
      return (
        '<button type="button" class="ref-tab' +
        (i === 0 ? " is-active" : "") +
        '" role="tab" data-ref-style="' +
        s.id +
        '" aria-selected="' +
        (i === 0 ? "true" : "false") +
        '">' +
        s.label +
        "</button>"
      );
    }).join("") +
    "</div>" +
    '<p class="ref-hint">Click a card to copy · links open in a new tab</p></div>' +
    '<div class="ref-list" role="list"></div>' +
    '<p class="ref-toast" role="status" aria-live="polite" hidden>Copied</p>';

  mount.querySelectorAll(".ref-tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setTab(btn.getAttribute("data-ref-style"));
    });
  });

  mount.addEventListener("click", function (e) {
    if (e.target.closest("a.ref-link")) return;
    var card = e.target.closest(".ref-card");
    if (card) copyCard(card);
  });

  mount.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var card = e.target.closest(".ref-card");
    if (!card) return;
    e.preventDefault();
    copyCard(card);
  });

  setTab("apa");
  mount.setAttribute("aria-busy", "false");
})();
