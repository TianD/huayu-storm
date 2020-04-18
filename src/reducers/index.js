import { combineReducers } from 'redux';
import { project_list, get_project_list_failed, get_project_list_loading } from './project_list';
import { overview_filters } from './overview';
import { mayabatch_filters, mayabatch_items } from './mayabatch';
import { nukebatch_filters, nukebatch_taskid, nukebatch_items } from './nukebatch';
import { seq2movbatch_filters, seq2movbatch_items } from './seq2movbatch';

const rootReducer = combineReducers({
    project_list,
    get_project_list_failed,
    get_project_list_loading,
    overview_filters,
    mayabatch_filters,
    mayabatch_items,
    nukebatch_filters,
    nukebatch_taskid,
    nukebatch_items,
    seq2movbatch_filters,
    seq2movbatch_items
});

export default rootReducer;
