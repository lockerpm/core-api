def paginate_queryset(queryset, paging: str = "1", page: int = 1, page_size: int = 10):
    try:
        total_record = queryset.count()
    except TypeError:
        total_record = len(queryset)
    if paging and paging == "1":
        page = max(page, 1)
        start_index = (page - 1) * page_size
        end_index = page_size * page
        if start_index < total_record:
            # Ensure the start index is within the range of total records
            start_index = min(start_index, total_record)
            end_index = min(end_index, total_record)
            queryset = queryset[start_index:end_index]
        else:
            queryset = []
    return queryset, total_record
