import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Table, Button, Upload, Select, Row, Col } from 'antd';
import { PlayCircleTwoTone, RestTwoTone } from '@ant-design/icons';
import {set_mayabatch_filters} from '../actions/mayabatch'

const {remote } = window.electron;

function mapStateToProps(state) {
    return {
        project_list: state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading,
        mayabatch_filters: state.mayabatch_filters
    }
}

function mapDispatchToProps(dispatch) {
    return {
        set_mayabatch_filters: (data)=>dispatch(set_mayabatch_filters(data))
    }
}

class BatchTableForMaya extends Component {

    constructor(props) {
        super(props)
        this.columns = [
            {
                title: 'Id',
                dataIndex: 'id',
                key: 'id',
            },
            {
                title: '状态',
                dataIndex: 'status',
                key: 'status',
            },
            {
                title: '文件',
                dataIndex: 'name',
                key: 'Name',
            },
            {
                title: 'Action',
                dataIndex: 'action',
                key: 'action',
                render: (text, record) => (
                    <span>
                        <Button onClick={()=>{this.playThis(record)}} 
                        style={{ margin: 3 }} ghost shape="circle" icon={<PlayCircleTwoTone twoToneColor="#52c41a" />} />
                        <Button onClick={()=>{this.removeThis(record)}} 
                        style={{ margin: 3 }} ghost shape="circle" icon={<RestTwoTone twoToneColor="#eb2f96" />} />
                    </span>
                )
            }
        ]
        this.state = {
            file_list: []
        }
    }

    playThis(record) {
        // TODO: 用maya进行处理
        console.log(record)
    }
    
    removeThis(record) {
        let {file_list} = this.state;
        file_list.splice(record.key, 1);
        let new_file_list = file_list.map((item, index)=>{
            return {...item, key: index, id: index+1}
        })
        this.setState({
            file_list: new_file_list
        })
    }

    async upload(e) {
        let result = await remote.dialog.showOpenDialog({
            properties: ['openFile'],
        });
        let file_list = [];
        for (let i = 0; i < result.filePaths.length; i++) {
            let file_data = {
                key: i,
                id: i + 1,
                name: result.filePaths[i],
                status: '就绪'
            }
            file_list.push(file_data)
        }
        this.setState({
            file_list: file_list
        })
    }

    clearlist(){
        this.setState({
            file_list: []
        })
    }

    change_project(value) {
        this.props.set_mayabatch_filters(value)
    }

    render() {
        let { file_list } = this.state;
        return (
            <div>
                <Row>
                    <Col span={6}>
                        <Select
                            options={this.props.project_list}
                            defaultValue={this.props.mayabatch_filters}
                            onChange={(value)=>{this.change_project(value)}}
                            style={{ margin: 12, width: 140 }} />
                            <Button onClick={(e)=>{this.upload(e)}} style={{ margin: 12 }}>选择文件</Button>
                    </Col>
                    <Col span={6} offset={12}>
                        <Button style={{ margin: 12 }} onClick={()=>{this.clearlist()}}>清空</Button>
                        <Button style={{ margin: 12 }}>全部开始</Button>
                    </Col>
                </Row>
                <Table
                    tableLayout={"fixed"}
                    dataSource={file_list}
                    columns={this.columns}
                    pagination={false}
                />
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(BatchTableForMaya);