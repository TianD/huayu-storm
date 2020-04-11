import { combineReducers } from 'redux';
import { project_list, get_project_list_failed, get_project_list_loading } from './project_list';
import { overview_filters } from './overview';
import { mayabatch_filters } from './mayabatch';
import { nukebatch_filters, nukebatch_taskid } from './nukebatch';
import { seq2movbatch_filters } from './seq2movbatch';

const rootReducer = combineReducers({
    project_list,
    get_project_list_failed,
    get_project_list_loading,
    overview_filters,
    mayabatch_filters,
    nukebatch_filters,
    nukebatch_taskid,
    seq2movbatch_filters,
});

export default rootReducer;
