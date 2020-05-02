import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Table, Row, Col, Radio, Cascader, Button } from 'antd';
import { PlayCircleTwoTone } from '@ant-design/icons';
import { set_nukebatch_filters, set_nukebatch_taskid, set_nukebatch_items } from '../actions/nukebatch';
import api from '../api'

function mapStateToProps(state) {
    return {
        project_list: state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading,
        nukebatch_filters: state.nukebatch_filters,
        nukebatch_taskid: state.nukebatch_taskid,
        nukebatch_items: state.nukebatch_items
    }
}

function mapDispatchToProps(dispatch) {
    return {
        set_nukebatch_filters: (data) => dispatch(set_nukebatch_filters(data)),
        set_nukebatch_taskid: (data) => dispatch(set_nukebatch_taskid(data)),
        set_nukebatch_items: (data) => dispatch(set_nukebatch_items(data))
    }
}

const taskmap = {
    1: '生成Nuke工程',
    2: '提交渲染'
}

class BatchTableForNuke extends Component {

    constructor(props) {
        super(props)
        this.columns = [
            {
                title: '镜头',
                dataIndex: 'key',
                key: 'key',
                width: 120
            },
            {
                title: '预览',
                dataIndex: 'preview',
                key: 'preview',
                width: 255,
                render: (text) => <img style={{ height: 75 }} src={api.get_thumbnail_url({ 'preview': text })} />
            },
            {
                title: '工程文件',
                dataIndex: 'nuke_project',
                key: 'nuke_project',
            },
            {
                title: '任务类型',
                dataIndex: 'taskid',
                key: 'taskid',
                render: (text) => taskmap[text]
            },
            {
                title: '状态',
                dataIndex: 'status',
                key: 'status'
            },
            {
                title: 'Action',
                dataIndex: 'action',
                key: 'action',
                width: 60,
                render: (text, record, index) => (
                    <span>
                        <Button onClick={() => this.playThis(record, index)} style={{ margin: 3 }} ghost shape="circle" icon={<PlayCircleTwoTone twoToneColor="#52c41a" />} />
                    </span>
                )
            }
        ]
    }

    changeTask(e) {
        let shots = this.props.nukebatch_items;
        let new_shot_list = shots.map((item) => {
            if (item.status === 'Ready') {
                return { ...item, taskid: e.target.value }
            }
            return item
        })
        this.props.set_nukebatch_taskid(e.target.value)
        this.props.set_nukebatch_items(new_shot_list)
    }

    async playThis(record, index) {
        let shots = this.props.nukebatch_items;
        await api.nuke_setup_process(record).then((response) => {
            let new_record = { ...record, ...response.data }
            shots.splice(index, 1, new_record)
        })
        this.props.set_nukebatch_items(shots)
    }

    async playAll() {
        let shots = this.props.nukebatch_items;
        let new_shots = [];
        for (let i = 0; i < shots.length; i++) {
            await api.nuke_setup_process(shots[i]).then((response) => { 
                new_shots.push({ ...shots[i], ...response.data }) 
            })
        }
        this.props.set_nukebatch_items(new_shots)
    }

    filterShots(value) {
        let current_taskid = this.props.nukebatch_taskid;
        let project_list = this.props.project_list;
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
        let new_shot_list = shot_list.map((item) => ({ ...item, taskid: current_taskid }))
        this.props.set_nukebatch_filters(value)
        this.props.set_nukebatch_items(new_shot_list)
    }

    render() {
        console.log(this.props.nukebatch_items)
        return (
            <div>
                <Row>
                    <Col span={6}>
                        <Cascader
                            placeholder="选择项目"
                            options={this.props.project_list}
                            defaultValue={this.props.nukebatch_filters}
                            onChange={(value) => { this.filterShots(value) }}
                            style={{ margin: 12 }} />
                    </Col>
                    <Col span={6} offset={6}>
                        <Radio.Group value={this.props.nukebatch_taskid} onChange={(e) => { this.changeTask(e) }} style={{ margin: 17 }}>
                            <Radio value={1} >生成Nuke工程</Radio>
                            <Radio value={2} >提交渲染</Radio>
                        </Radio.Group>

                    </Col>
                    <Col span={6}><Button style={{ margin: 12 }} onClick={() => { this.playAll() }}>全部开始</Button></Col>
                </Row>
                <Table
                    tableLayout={"fixed"}
                    dataSource={this.props.nukebatch_items}
                    columns={this.columns}
                    pagination={false}
                    size="small"
                    bordered
                />
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(BatchTableForNuke)