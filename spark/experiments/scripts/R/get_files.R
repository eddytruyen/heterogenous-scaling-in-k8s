

get_files <- function(directory) {
  #all_files=list.files(path=directory, recursive=TRUE)
  files.names <- seq(1,10)
  files <- vector("list", length(files.names))
  names(files) <- files.names
  for (i in files.names) {
    files[[i]] <- list.files(path=directory, pattern=paste("-t",i,".csv",sep=""), recursive=TRUE)
  }
  return (files)
}