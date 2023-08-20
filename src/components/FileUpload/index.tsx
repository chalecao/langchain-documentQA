import { ChangeEvent, useState, useRef } from 'react';
import Style from './index.module.css';

export default function ({ uploadRef, afterFileUpload }) {

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const file = e.target.files[0];
            var formData = new FormData();
            formData.append('file', file);

            fetch('http://127.0.0.1:3006/api/v1/upload', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    console.log('File uploaded:', data);
                    if (data && data.filename) {
                        afterFileUpload({
                            filename: data.filename,
                            size: file.size,
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    };

    return (
        <div>
            <input ref={uploadRef} type="file" className={Style.hidden} onChange={handleFileChange} />
        </div>
    );
}
