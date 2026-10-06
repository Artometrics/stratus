#show: doc => article(
$if(mainfont)$
  font: ("$mainfont$",),
  heading-family: ("$mainfont$",),
$endif$
$if(fontsize)$
  fontsize: $fontsize$,
$endif$
$if(lang)$
  lang: "$lang$",
$endif$
$if(section-numbering)$
  sectionnumbering: "$section-numbering$",
$endif$
$if(toc)$
  toc: $toc$,
$endif$
$if(toc-title)$
  toc_title: [$toc-title$],
$endif$
  toc_depth: $toc-depth$,
  cols: $if(columns)$$columns$$else$1$endif$,
  doc
)
