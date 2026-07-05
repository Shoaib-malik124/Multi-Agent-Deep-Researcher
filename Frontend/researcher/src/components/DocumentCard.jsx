import ReportDownload from "./ReportDownload"

export const DocumentCard = ({ doc }) => {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 
                        hover:shadow-md transition cursor-pointer">
            <h3 className="font-semibold text-gray-800 truncate">{doc.query}</h3>
            <p className="text-sm text-gray-400 mt-1">
                {new Date(doc.created_at).toLocaleDateString()}
            </p>
            <ReportDownload content={doc.content} />
        </div>
    )
}