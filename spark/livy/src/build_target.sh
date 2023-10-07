livy_dir="."
built_dir="./built_livy"

# Check if the directory exists, and if so, remove it.
if [ -d "$built_dir" ]; then
    rm -r "$built_dir"
    echo "Removed the $built_dir directory."
fi

# If the directory doesn't exist, create it.
if [ ! -d "$built_dir" ]; then
    mkdir "$built_dir"
    echo "Created the $built_dir directory."
fi

# Specify subdirectories for various Livy artifacts.
built_jars="$built_dir/jars"
built_rcs_jars="$built_dir/rsc-jars"
built_repl_jars="$built_dir/repl_2.12-jars"

# Copy certain files and directories from the Livy directory to the built directory.
cp "$livy_dir/DISCLAIMER" "$built_dir/"
cp "$livy_dir/LICENSE" "$built_dir/"
cp "$livy_dir/NOTICE" "$built_dir/"
cp -rf "$livy_dir/bin" "$built_dir/"
cp -rf "$livy_dir/conf" "$built_dir/"

# Create a directory for Livy JAR files.
mkdir "$built_jars"

# Find all JAR files in the Livy directory and copy them to the JARs directory.
cp server/target/jars/* $built_jars
cp thriftserver/server/target/jars/* $built_jar

# Create a directory for REPL JAR files.
mkdir "$built_repl_jars"

# Copy REPL JAR files from a specific location in the Livy directory to the REPL JARs directory.
cp -rf "$livy_dir/repl/scala-2.12/target/jars"/* "$built_repl_jars/"

sed -i 's/repl-2.11/repl-2.12/g/' ${built_dir}/bin/livy-server 

# Create a directory for RSC JAR files.
mkdir "$built_rcs_jars"

# Copy specific JAR files related to Livy and dependencies to the RSC JARs directory.
find "$built_jars" -name "*livy-api*.jar" -exec cp {} "$built_rcs_jars" \;
find "$built_jars" -name "*livy-rsc*.jar" -exec cp {} "$built_rcs_jars" \;
find "$built_jars" -name "*livy-thriftserver*.jar" -exec cp {} "$built_rcs_jars" \;
find "$built_jars" -name "*netty-all*.jar" -exec cp {} "$built_rcs_jars" \;
