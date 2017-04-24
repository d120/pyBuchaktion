import io
import csv

def net_library_csv(queryset):
    out_stream = io.StringIO()
    writer = csv.writer(out_stream, delimiter='|', quotechar="\"", quoting=csv.QUOTE_MINIMAL)
    for order in queryset:
        array = [
            order.student.library_id,
            order.book.author,
            order.book.title,
            order.book.publisher,
            order.book.year,
            order.book.isbn_13
        ]
        writer.writerow(array)

    return out_stream.getvalue()
