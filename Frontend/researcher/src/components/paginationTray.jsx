export const PaginationTray = ({ currentPage, totalPages, onPageChange }) => {
    return (
        <div className="flex items-center justify-center gap-4 mt-8 pb-6">
            {/* Previous button */}
            <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-4 py-2 rounded-lg bg-gray-200 disabled:opacity-50 
                           disabled:cursor-not-allowed hover:bg-gray-300 transition"
            >
                ← Previous
            </button>

            {/* Page indicator */}
            <span className="text-sm text-gray-600">
                Page {currentPage} of {totalPages}
            </span>

            {/* Next button */}
            <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-4 py-2 rounded-lg bg-gray-200 disabled:opacity-50 
                           disabled:cursor-not-allowed hover:bg-gray-300 transition"
            >
                Next →
            </button>
        </div>
    )
}