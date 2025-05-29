#!/bin/bash

# Prompt for start and end dates
read -p "Enter start date (YYYY-MM-DD): " since_date
read -p "Enter end date (YYYY-MM-DD): " until_date

# Extract the month name from the start date for the title
# This assumes the start and end dates are within the same month for a clean title.
# If they span multiple months, you might want to adjust the title logic.
report_month=$(date -d "$since_date" +%B) # e.g., "May"

# Define report and graph file names
report_file="Subesh_Commits_${since_date}_to_${until_date}"
summary_txt="${report_file}.txt"
graph_data="${report_file}_graph.dat"
line_graph_png="${report_file}_line_graph.png"
bar_graph_png="${report_file}_bar_graph.png"
awk_script_file=$(mktemp) # Create a temporary file for the awk script

# --- Step 1: Extract commit data and count files ---
echo "Generating commit summary..."
echo "Subesh's Git Commit Summary ($since_date to $until_date)" > "$summary_txt"
echo "------------------------------------------------------" >> "$summary_txt"

git log --author="Subesh" --since="$since_date" --until="$until_date" \
  --pretty=format:"%h|%ad|%s" --date=short --name-only | \
awk -F"|" '
  /^[0-9a-f]{7}\|/ {
    if (commit != "") {
      print "Files changed: " filecount "\n" >> "'"$summary_txt"'"
    }
    split($0, arr, "|")
    commit=arr[1]
    date=arr[2]
    msg=arr[3]
    print "Commit: " commit >> "'"$summary_txt"'"
    print "Date  : " date >> "'"$summary_txt"'"
    print "Msg   : " msg >> "'"$summary_txt"'"
    filecount=0
    next
  }
  NF { filecount++ }
  END {
    if (commit != "") {
      print "Files changed: " filecount "\n" >> "'"$summary_txt"'"
    }
  }
'

# --- Step 2: Create graph data for gnuplot with dates ---
echo "Preparing graph data with dates..."
echo "# Date FilesChanged" > "$graph_data"

# Write the awk script to a temporary file
cat << 'EOF_AWK_SCRIPT' > "$awk_script_file"
BEGIN { files_changed_per_date[""] = 0 } # Initialize to avoid issues with first entry
/^COMMIT_SEP:/ {
  # If a previous date was being processed, print its count
  if (current_date != "" && current_date != "COMMIT_SEP:") {
    print current_date, files_changed_per_date[current_date]
  }
  # Extract the new date
  current_date = substr($0, length("COMMIT_SEP:") + 1)
  # Initialize count for the new date if it's the first time we see it
  if (!(current_date in files_changed_per_date)) {
    files_changed_per_date[current_date] = 0
  }
  next # Move to the next line
}
# If it's not a COMMIT_SEP line, it must be a filename
NF > 0 { # Ensure it's not an empty line
  files_changed_per_date[current_date]++
}
END {
  # Print the count for the last processed date
  if (current_date != "" && current_date != "COMMIT_SEP:") {
    print current_date, files_changed_per_date[current_date]
  }
}
EOF_AWK_SCRIPT

# Execute git log and pipe its output to the temporary awk script
git log --author="Subesh" --since="$since_date" --until="$until_date" \
  --pretty=format:"COMMIT_SEP:%ad" --date=format:"%Y-%m-%d" --name-only | \
awk -f "$awk_script_file" | sort -k1,1 > "$graph_data"

# --- Step 3: Generate PNG line chart with enhanced styling ---

echo "Creating line graph image..."
gnuplot <<EOF
set terminal pngcairo size 1400,700 enhanced font 'Arial,12' # Larger canvas, slightly bigger base font
set output "$line_graph_png"
set title "Number of Files Changed per Commit (Subesh)\n${report_month} ${since_date} to ${until_date}" font 'Arial,14,bold' # Bold title
set xlabel "Day of Month" font 'Arial,11' offset 0,-2 # Shift xlabel down slightly
set ylabel "Files Changed" font 'Arial,11'
set xdata time
set timefmt "%Y-%m-%d"
set format x "%d" # Show only the day
set autoscale xfix
set xtics rotate by 45 offset 0,-1 font 'Arial,9' # Smaller font, shift labels down
set xtics 86400 # One tic per day (86400 seconds), adjust if needed
set mxtics 2 # Minor ticks for better scaling
set grid xtics mxtics ytics lt 1 lc rgb "#e0e0e0" # Light gray grid for better contrast
set bmargin at screen 0.2 # Larger bottom margin for rotated labels
set style data linespoints
set style line 1 linecolor rgb "#1f77b4" linewidth 3 pointtype 7 pointsize 1.5 # Thicker line, larger points
set key top left font 'Arial,10' box lc rgb "#000000" # Legend with border
plot "$graph_data" using 1:2 title "Files Changed" with linespoints linestyle 1
EOF

# --- Step 4: Generate PNG bar chart with enhanced styling ---
# --- Step 4: Generate PNG bar chart with enhanced styling ---
echo "Creating bar graph image..."
gnuplot <<EOF
set terminal pngcairo size 1400,700 enhanced font 'Arial,12' # Larger canvas, slightly bigger base font
set output "$bar_graph_png"
set title "Number of Files Changed per Commit (Subesh) - Bar Graph\n${report_month} ${since_date} to ${until_date}" font 'Arial,14,bold' # Bold title
set xlabel "Day of Month" font 'Arial,11' offset 0,-2 # Shift xlabel down
set ylabel "Files Changed" font 'Arial,11'
set xdata time
set timefmt "%Y-%m-%d"
set format x "%d" # Show only the day
set style fill solid 0.7 border lc rgb "#333333" # Slightly more opaque, dark border
set boxwidth 0.6 relative # Slightly narrower bars
set xtics rotate by 45 offset 0,-1 font 'Arial,9' # Smaller font, shift labels down
set xtics 86400 # One tic per day, adjust if needed
set mxtics 2 # Minor ticks
set grid xtics mxtics ytics lt 1 lc rgb "#e0e0e0" # Light gray grid
set bmargin at screen 0.2 # Larger bottom margin for rotated labels
set key off # No legend for bar graph
plot "$graph_data" using 1:2 with boxes title "Files Changed" fillcolor rgb "#ff7f0e"
EOF

# --- Cleanup ---
rm "$graph_data" "$awk_script_file" # Remove temporary files

echo "PNG line graph generated: $line_graph_png"
echo "PNG bar graph generated: $bar_graph_png"