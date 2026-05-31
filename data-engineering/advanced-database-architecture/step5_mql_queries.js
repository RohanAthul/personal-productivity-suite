use('database_architects_unstructured');

// Which are the top 3 meetings with the highest number of speakers?
const q1 = db.transcripts.find(
  {},
  { meeting_id: 1, city: 1, speaker_count: 1 }
)
.sort({ speaker_count: -1 })
.limit(5)
.toArray();

// What is the average meeting transcript length in each city?
const q2 = db.transcripts.aggregate([
  {
    $group: {
      _id: "$city",
      avgTranscriptLength: { $avg: "$transcript_word_count" }
    }
  },
  {
    $project: {
      City: "$_id",
      AvgTranscriptLength: { $round: ["$avgTranscriptLength", 0] },
      _id: 0
    }
  }
]).toArray();


// Average number of speakers per city
const q3 = db.transcripts.aggregate([
  {
    $group: {
      _id: "$city",
      avgSpeakers: { $avg: "$speaker_count" }
    }
  }
]).toArray();

// Meetings that mention “budget” or “housing” - grouped by city
const q4 = db.transcripts.aggregate([
  {
    $match: {
      $or: [
        { full_transcript_text: /budget/i },
        { full_transcript_text: /housing/i }
      ]
    }
  },
  {
    $group: {
      _id: "$city",
      mentionCount: { $sum: 1 }
    }
  },
  { $sort: { mentionCount: -1 } }
]).toArray();

// Longest meeting per city (highest word count)
const q5 = db.transcripts.aggregate([
  {
    $sort: { transcript_word_count: -1 }
  },
  {
    $group: {
      _id: "$city",
      meeting_id: { $first: "$meeting_id" },
      topWords: { $first: "$transcript_word_count" }
    }
  }
]).toArray();

// Which city has more meetings overall?
const q6 = db.transcripts.aggregate([
  {
    $group: {
      _id: "$city",
      totalMeetings: { $sum: 1 }
    }
  },
  { $sort: { totalMeetings: -1 } }
]).toArray();

// Calculate average transcript length per city
const q7 = db.transcripts.aggregate([
  {
    $group: {
      _id: "$city",
      avgTranscriptLength: { $avg: "$transcript_word_count" }
    }
  },
  {
    $project: {
      City: "$_id",
      AvgTranscriptLength: { $round: ["$avgTranscriptLength", 0] },
      _id: 0
    }
  }
]).toArray();

//  Rank meetings by transcript length (largest first) (Top 5 only)
const q8 = db.transcripts.aggregate([
  {
    $setWindowFields: {
      sortBy: { transcript_word_count: -1 },
      output: {
        rank: { $rank: {} }
      }
    }
  },
  {
    $project: {
      meeting_id: 1,
      city: 1,
      transcript_word_count: 1,
      rank: 1,
      _id: 0
    }
  },
  { $limit: 5 }
]).toArray();


//  Top 10 longest meetings overall
const q9 = db.transcripts.find(
  {},
  { meeting_id: 1, city: 1, transcript_word_count: 1 }
)
.sort({ transcript_word_count: -1 })
.limit(10)
.toArray();

// OUTPUT: code taken from AI
// --- 🛠️ THE DATAFRAME HELPER FUNCTION ---
function printDataFrame(title, data) {
  if (!data || data.length === 0) {
    console.log(`\n--- ${title}: No Data Available ---`);
    return;
  }

  // 1. Extract headers (column names)
  const headers = Object.keys(data[0]);

  // 2. Calculate the width needed for each column
  const colWidths = {};
  headers.forEach(header => {
    const maxWidth = Math.max(
      header.length,
      ...data.map(row => String(row[header] !== undefined ? row[header] : "").length)
    );
    colWidths[header] = maxWidth;
  });

  // 3. Create the table parts
  const createRow = (row) => headers.map(h => String(row[h] ?? "").padEnd(colWidths[h])).join("  |  ");
  const headerRow = headers.map(h => h.toUpperCase().padEnd(colWidths[h])).join("  |  ");
  const divider = "-".repeat(headerRow.length);

  // 4. Print the "DataFrame"
  console.log(`\n[ ${title.toUpperCase()} ]`);
  console.log(divider);
  console.log(headerRow);
  console.log(divider);
  data.forEach(row => console.log(createRow(row)));
  console.log(divider);
  console.log(`Rows: ${data.length}\n`);
}

// --- DISPLAY ALL RESULTS ---

printDataFrame("Q1 Top 3 Meetings by Speaker Count", q1);

printDataFrame("Q2 Avg Meeting Length by City", q2);

printDataFrame("Q3 Avg Speakers per City", q3.map(item => ({
    City: item._id, 
    AvgSpeakers: item.avgSpeakers.toFixed(2) 
})));

printDataFrame("Q4 Budget/Housing Mentions", q4);

printDataFrame("Q5 Longest Meeting per City", q5);

printDataFrame("Q6 City Meeting Counts", q6);

printDataFrame("Q7 Average Transcript Length per City", q7);

printDataFrame("Q8 Meeting Rank by Transcript Length", q8);

printDataFrame("Q9 Top 10 Longest Meetings", q9);
