import React, {Component} from 'react';
import {Button, Card, Col, Row} from 'antd';
import {PictureOutlined} from '@ant-design/icons';
import api from '../api'

const {Meta} = Card;

class MyCard extends Component {

    componentDidMount() {

    }

    render() {
        return (
            <Card
                hoverable
                style={{width: 300}}
                type={"inner"}
                cover={
                    <div
                        style={{textAlign: "center"}}
                    >
                        <img
                            // style={{width: "auto", maxHeight: 185}}
                            style={{maxHeight: 185, maxWidth: 300, height: "auto", width: "auto"}}
                            alt="example"
                            src={api.get_thumbnail_url(this.props.shot)}
                        />
                    </div>
                }
                onClick={(event) => this.props.onClick(event)}
            >
                <Meta title={this.props.shot["label"]}/>
            </Card>
        )
    }
}

export default MyCard