import React from "react";

const ReportDownload = ({content="I am a deep research content"}) => {
    const onButtonClick = () => {
        const blob=new Blob([content],{type:'text/markdown'})
        const url=URL.createObjectURL(blob)
        const link = document.createElement("a");
        link.href = url;
        link.download = "research_report.md";
        link.click();
        URL.revokeObjectURL(url)
    };
    return (
        <>
            <button
                onClick={onButtonClick}
                className="mt-2 flex items-center gap-1 
                        bg-blue-600 hover:bg-blue-700 text-white text-xs
                        font-medium py-1.5 px-3 rounded-lg transition"
            >
                Download ↓
            </button>
        </>
    );
};

export default ReportDownload;