

get_sorted_runs <- function(directory) {
  #all_files=list.files(path=directory, recursive=TRUE)
  files.names <- seq(1,10)
  files <- vector("list", length(files.names))
  names(files) <- files.names
  for (i in files.names) {
    files[[i]] <- list.files(path=directory, pattern=paste("-t",i,".csv",sep=""), recursive=TRUE)
  }
  return (files)
}

get_sorted_runs_vpa <- function(directory) {
  #all_files=list.files(path=directory, recursive=TRUE)
  files.names <- c("1","2","3","4","4b","5","5b")
  files <- vector("list", length(files.names))
  names(files) <- files.names
  for (i in files.names) {
    files[[i]] <- list.files(path=directory, pattern=paste("-t",i,".csv",sep=""), recursive=TRUE)
  }
  return (files)
}