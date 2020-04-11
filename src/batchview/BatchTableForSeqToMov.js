import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Table, Upload, Button, Select, Col, Row } from 'antd';
import { PlayCircleTwoTone, RestTwoTone } from '@ant-design/icons';
import { set_seq2movbatch_filters } from '../actions/seq2movbatch'

function mapStateToProps(state) {
    return {
        project_list: state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading,
        seq2movbatch_filters: state.seq2movbatch_filters
    }
}

function mapDispatchToProps(dispatch) {
    return {
        set_seq2movbatch_filters: (data) => dispatch(set_seq2movbatch_filters(data))
    }
}


const dataSource = [
    {
        key: '1',
        id: 1,
        status: '就绪',
        shot: 'EP509_s001_cp_001.mov',
        thumbnail: "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png",
        taskType: 'Nuke模板',
    },
    {
        key: '2',
        id: 2,
        status: '就绪',
        shot: 'EP509_s002_cp_001.mov',
        thumbnail: "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png",
        taskType: 'Nuke模板',
    },
]

class BatchTableForSeqToMov extends Component {

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

    change_project(value){
        this.props.set_seq2movbatch_filters(value)
    }

    clearlist(){
        this.setState({
            file_list: []
        })
    }

    render() {
        return (
            <div>
                <Row>
                    <Col span={6}>
                        <Select
                            placeholder="选择项目"
                            options={this.props.project_list}
                            defaultValue={this.props.seq2movbatch_filters}
                            onChange={(value)=>this.change_project(value)}
                            style={{ margin: 12, width: 140 }} />
                        <Upload
                            showUploadList={false}>
                            <Button style={{ margin: 12 }}>选择文件</Button>
                        </Upload>
                    </Col>
                    <Col span={6} offset={12}>
                        <Button style={{ margin: 12 }}>清空</Button>
                        <Button style={{ margin: 12 }}>全部开始</Button>
                    </Col>
                </Row>
                <Table
                    tableLayout={"fixed"}
                    dataSource={dataSource}
                    columns={this.columns}
                    pagination={false}
                />
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(BatchTableForSeqToMov)