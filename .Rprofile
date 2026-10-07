extra_paths <- c(
  "/Users/kylemcauliffe/Library/R/arm64/4.6/library",
  "/Library/Frameworks/R.framework/Versions/4.6/Resources/library"
)
existing_paths <- extra_paths[dir.exists(extra_paths)]
if (length(existing_paths) > 0) {
  .libPaths(unique(c(.libPaths(), existing_paths)))
}
