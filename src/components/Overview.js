import React, { Component } from 'react';
import { Cascader, List } from 'antd';
import { connect } from 'react-redux';
import MyCard from './MyCard';
import DetailView from './DetailView';
import {set_overview_filters} from '../actions/overview'


function mapStateToProps(state) {
    return {
        project_list:state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading,
        overview_filters: state.overview_filters
    }
}

function mapDispatchToProps(dispatch) {
    return {
        set_overview_filters: (data)=>dispatch(set_overview_filters(data))
    }
}

class Overview extends Component {
    constructor(props) {
        super(props)
        this.state = {
            visible: false,
            shots: [],
            current_shot: {}
        }
    }

    changeVisible = (flag) => {
        this.setState({
            visible: flag
        })
    }

    onCardClick(item) {
        this.setState({
            current_shot: item
        },
            this.changeVisible(true))
    }

    filterShots = (value) => {
        this.props.set_overview_filters(value)
        let project_list = this.props.project_list
        let shot_list;
        if (value.length > 0) {
            let project = project_list.filter((element) => {
                return element["value"] === value[0]
            })[0]
            let episode = project["children"].filter((element) => {
                return element["value"] === value[1]
            })[0]
            if (value[1] === 'all') {
                shot_list = episode["shots"]
            } else {
                let sequence = episode["children"].filter((element) => {
                    return element["value"] === value[2]
                })[0]
                shot_list = sequence["shots"]
            }
        } else {
            shot_list = [];
        }
        this.setState({
            shots: shot_list
        })
    }

    componentDidMount(){
        this.filterShots(this.props.overview_filters)
    }

    render() {
        let { visible, shots, current_shot } = this.state;
        return (
            <div>
                <Cascader
                defaultValue = {this.props.overview_filters}
                    style={{ position: 'absolute', left: '30px' }}
                    options={this.props.project_list}
                    onChange={(value) => this.filterShots(value)}
                    placeholder="Please select" />
                <div style={{ padding: '50px' }}>
                    <List
                        itemLayout={'horizontal'}
                        dataSource={shots}
                        grid={{ gutter: 36, lg: 4, md: 3, sm: 1, xs: 1 }}
                        renderItem={
                            item => (
                                <List.Item>
                                    <MyCard shot={item} onClick={(e) => this.onCardClick(item)} />
                                </List.Item>
                            )
                        }
                    >
                    </List>
                </div>
                <DetailView shot={current_shot} visible={visible} changeVisible={this.changeVisible}/>
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Overview);