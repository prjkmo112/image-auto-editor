class Tools {
  private static instance: Tools;

  private constructor() {

  }

  public static getInstance():Tools {
    if (!Tools.instance)
      Tools.instance = new Tools();

    return Tools.instance;
  }

  getValue(content:string, rule:string|RegExp) {
    var value = '';
    var regex = new RegExp(rule, "img"); // 정규식

    var match = regex.exec(content);
    if (match)
      value = match[1].trim();

    return value;
  }

  getValues(content:string, rule:string|RegExp) {
    var value, value2;
    var valueList = new Array();
    var regex = new RegExp(rule, "img"); // 정규식

    do {
      var match = regex.exec(content);
      if (match) {
        value = match[1].trim();

        if (match.length <= 2) {
          valueList.push(value);
        } else {
          value2 = match[2].trim();
          valueList.push({value : value, value2 : value2});
        }
      }
    } while(match);

    return valueList;
  }

}

const tools = Tools.getInstance();

export default tools;