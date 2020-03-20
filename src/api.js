import axios from 'axios';

axios.defaults.baseURL = 'http://127.0.0.1:5000/api'


class Api {

    get_project_list(callback) {
        axios.get('/get_project_list')
        .then(callback)
    }

}

const api = new Api()

export default api