/* Quarto Typst preamble — DM Sans, logo footer */

#set text(font: "DM Sans", size: 10.5pt, fill: rgb("#1e293b"))

#show heading.where(level: 1): set text(font: "DM Sans", weight: "bold", size: 15pt, fill: rgb("#1e293b"))
#show heading.where(level: 2): set text(font: "DM Sans", weight: "bold", size: 12.5pt, fill: rgb("#1e293b"))
#show heading.where(level: 3): set text(font: "DM Sans", weight: 500, size: 11pt, fill: rgb("#1e293b"))

#set page(
  paper: "us-letter",
  margin: (left: 0.7in, right: 0.7in, top: 0.7in, bottom: 0.78in),
  footer: context {
    if counter(page).get().first() > 1 {
      set text(size: 8pt, fill: rgb("#64748b"), font: "DM Sans")
      grid(
        columns: (1fr, auto, 1fr),
        align: (left, center, right),
        [CMS TEAM briefing],
        counter(page).display("1"),
        box(height: 13pt, image("assets/rainfall-logo.png")),
      )
    }
  },
)

#set par(justify: true, leading: 0.62em)
