#!/bin/bash

database_file="$1"
if [[ ! -f "$database_file" ]]; then
	"The specified database file <$database_file> does not exist!" >&2
fi

set -o errexit
set -o nounset

sqlite="/usr/bin/sqlite3"

sql() {
	$sqlite "$database_file" "$1"
}

test_books=(
	" 1, '1234567890001', 'Book  1', 'AC', 'Author  1',  1.01"
	" 2, '1234567890002', 'Book  2', 'RJ', 'Author  2',  2.02"
	" 3, '1234567890003', 'Book  3', 'PP', 'Author  3',  3.03"
	" 4, '1234567890004', 'Book  4', 'OL', 'Author  4',  4.04"
	" 5, '1234567890005', 'Book  5', 'AC', 'Author  5',  5.05"
	" 6, '1234567890006', 'Book  6', 'RJ', 'Author  6',  6.06"
	" 7, '1234567890007', 'Book  7', 'PP', 'Author  7',  7.07"
	" 8, '1234567890008', 'Book  8', 'OL', 'Author  8',  8.08"
	" 9, '1234567890009', 'Book  9', 'AC', 'Author  9',  9.09"
	"10, '1234567890010', 'Book 10', 'RJ', 'Author 10', 10.10"
	"11, '1234567890011', 'Book 11', 'PP', 'Author 11', 11.11"
	"12, '1234567890012', 'Book 12', 'OL', 'Author 12', 12.12"
	"13, '1234567890013', 'Book 13', 'AC', 'Author 13', 13.13"
	"14, '1234567890014', 'Book 14', 'RJ', 'Author 14', 14.14"
	"15, '1234567890015', 'Book 15', 'PP', 'Author 15', 15.15"
)
test_order=(
	"1, 'PD', 'Hint 1', 12, 1, 1"
	"2, 'OD', 'Hint 2', 13, 1, 2"
	"3, 'RJ', 'Hint 3',  1, 1, 3"
	"4, 'AR', 'Hint 4',  2, 2, 1"
	"5, 'PD', 'Hint 5', 11, 2, 2"
	"6, 'OD', 'Hint 6',  6, 2, 3"
	"7, 'RJ', 'Hint 7', 12, 3, 1"
	"8, 'AR', 'Hint 8',  3, 4, 2"
	"9, 'PD', 'Hint 9',  7, 4, 3"
)
test_ordertimeframe=(
	"1, DATE('2017-01-01'), DATE('2017-01-31'), 30, 2"
	"2, DATE('2016-05-01'), DATE('2017-05-31'), 15, 1"
	"3, DATE('2017-02-01'), DATE('2017-02-28'), 12, 2"
	"4, DATE('2017-06-01'), DATE('2017-06-30'), 10, 3"
)
test_semester=(
	"1, 'S', 2016, 1000"
	"2, 'W', 2017, 2000"
	"3, 'S', 2017, 1500"
)
test_student=(
	"1"
	"2"
	"3"
)
test_tucanmodule=(
	" 1, '20-00-0001-iv', 'Module  1', 1"
	" 2, '20-00-0002-iv', 'Module  2', 2"
	" 3, '20-00-0003-iv', 'Module  3', 3"
	" 4, '20-00-0004-iv', 'Module  4', 1"
	" 5, '20-00-0005-iv', 'Module  5', 2"
	" 6, '20-00-0006-iv', 'Module  6', 3"
	" 7, '20-00-0007-iv', 'Module  7', 1"
	" 8, '20-00-0008-iv', 'Module  8', 2"
	" 9, '20-00-0009-iv', 'Module  9', 3"
	"10, '20-00-0010-iv', 'Module 10', 1"
	"11, '20-00-0011-iv', 'Module 11', 2"
	"12, '20-00-0012-iv', 'Module 12', 3"
	"13, '20-00-0013-iv', 'Module 13', 1"
	"14, '20-00-0014-iv', 'Module 14', 2"
	"15, '20-00-0015-iv', 'Module 15', 3"
)
test_tucanmodule_literature=(
	" 1,  3,  5"
	" 2,  5, 11"
	" 3,  4, 10"
	" 4,  3,  9"
	" 5, 11,  5"
	" 6,  3,  6"
	" 7, 14,  5"
	" 8, 12,  1"
	" 9,  7,  5"
	"10, 14,  7"
	"11, 15,  7"
	"12,  7,  9"
	"13,  2, 15"
	"14,  9, 12"
	"15, 13, 14"
	"16,  2, 11"
	"17, 10, 15"
	"18,  3,  3"
	"19,  4,  7"
	"20, 11,  9"
)

for book in "${test_books[@]}"; do
	sql "INSERT OR REPLACE INTO pyBuchaktion_book (id, isbn_13, title, state, author, price) VALUES ($book)"
done
for book in "${test_order[@]}"; do
	sql "INSERT OR REPLACE INTO pyBuchaktion_order (id, status, hint, book_id, order_timeframe_id, student_id) VALUES ($book)"
done
for ordertimeframe in "${test_ordertimeframe[@]}"; do
	sql "INSERT OR REPLACE INTO pyBuchaktion_ordertimeframe (id, start_date, end_date, spendings, semester_id) VALUES ($ordertimeframe)"
done
for semester in "${test_semester[@]}"; do
	sql "INSERT OR REPLACE INTO pyBuchaktion_semester (id, season, year, budget) VALUES ($semester)"
done
for student in "${test_student[@]}"; do
	sql "INSERT OR REPLACE INTO pyBuchaktion_student (id) VALUES ($student)"
done
for tucanmodule in "${test_tucanmodule[@]}"; do
	sql "INSERT OR REPLACE INTO pyBuchaktion_tucanmodule (id, module_id, name, last_offered_id) VALUES ($tucanmodule)"
done
for tucanmodule_literature in "${test_tucanmodule_literature[@]}"; do
	sql "INSERT OR REPLACE INTO pyBuchaktion_tucanmodule_literature (id, tucanmodule_id, book_id) VALUES ($tucanmodule_literature)"
done
