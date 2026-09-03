import axios from "axios";


const API_BASE_URL = 'http://localhost:8000';

export const services = {

    // get all docs 
    // upload doc
    async uploadDoc(file: File | null, title?: string) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        if (title) {
            formData.append('title', title);
        }

        try {
            const response = await axios.post(`${API_BASE_URL}/documents`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            console.error('Error uploading document:', error);
            throw error;
        }
    }

}